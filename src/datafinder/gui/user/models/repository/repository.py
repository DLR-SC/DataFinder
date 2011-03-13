# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
#Redistribution and use in source and binary forms, with or without
# All rights reserved.
#modification, are permitted provided that the following conditions are
#met:
#
#
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer. 
#
# * Redistributions in binary form must reproduce the above copyright 
#   notice, this list of conditions and the following disclaimer in the 
#   documentation and/or other materials provided with the 
#   distribution. 
#
# * Neither the name of the German Aerospace Center nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
#OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  


""" 
Qt-specific abstraction of the model of the data repository.
"""


__version__ = "$Revision-Id:$" 


import operator
import sys
from types import StringTypes

from PyQt4 import QtCore

from datafinder.common.logger import getDefaultLogger
from datafinder.core.error import ItemError
from datafinder.core.item.base import ItemBase
from datafinder.core.item.data_persister.constants import ITEM_STATE_ARCHIVED, \
                                                          ITEM_STATE_ARCHIVED_MEMBER, ITEM_STATE_ARCHIVED_READONLY, \
                                                          ITEM_STATE_MIGRATED, ITEM_STATE_UNSUPPORTED_STORAGE_INTERFACE, \
                                                          ITEM_STATE_INACCESSIBLE
from datafinder.gui.user.common.util import determineDisplayRepresentation, startNewQtThread, \
                                            determinePropertyDefinitionToolTip
from datafinder.gui.user.models.repository.action_handler import ActionHandler
from datafinder.gui.user.models.repository.history import HistoryModel
from datafinder.gui.user.models.repository.icon_provider import IconProvider


class RepositoryModel(HistoryModel):
    """ Implements the Qt-specific model for a data repository and its items. """
    
    def __init__(self, preferences):
        """ 
        Constructor. 
        
        @param repositoryManager: The central preferences.
        @type repositoryManager: L{PreferencesHandler<datafinder.core.configuration.preferences.PreferencesHandler>}
        """
        
        HistoryModel.__init__(self)
        self._headers = list()
        self._headerIds = list()
        
        self._repository = None
        self._actionHandler = None
        self._preferences = preferences
        self._iconProvider = None
        
        self._emptyQVariant = QtCore.QVariant()
        self._emptyQModelIndex = QtCore.QModelIndex()
        self._placeHolderCollection = ItemBase("...")
        self._placeHolderCollection._isCollection = True
        self._placeHolderLeaf = ItemBase("...")
        
        self._childrenPopulator = _ChildrenPopulator(self)
        self._lockedItems = list()
        
    def load(self, repository):
        """ 
        Loads the model.
        
        @param repository: The data repository.
        @type repository: L{Repository<datafinder.core.repository.Repository>}
        """
        
        self._actionHandler = ActionHandler(self, repository)
        self._headers = [self.tr("Name")]
        self._headerIds = ["name"]
        self._iconProvider = IconProvider(repository.configuration)
        systemPropertyDefinitions = sorted(repository.configuration.systemPropertyDefinitions,
                                           key=operator.attrgetter("displayName"))
        for propertyDefinition in systemPropertyDefinitions:
            self._headers.append(self.tr(propertyDefinition.displayName))
            self._headerIds.append(propertyDefinition.identifier)
        
        self._repository = repository
        self.activeIndex = self._emptyQModelIndex
        self.reset()

    def lock(self, indexes):
        """ Locks the given index. """

        # determine paths which are not required to be locked as
        # the parent is going to be locked either.
        items = list()
        invalidPaths = list()
        for index in indexes:
            items.append(self.nodeFromIndex(index))
        currentItem = self.nodeFromIndex(self.activeIndex) # this is done to protect the current item
        items.append(currentItem)
        
        for item1 in items:
            for item2 in items:
                if item1.path != item2.path:
                    if item1.path.startswith(item2.path) \
                       and not item2.path in invalidPaths:
                        invalidPaths.append(item1.path)
        items.remove(currentItem)
        if currentItem.path in invalidPaths: # prevent invalidation of current item 
            self.activeIndex = self._emptyQModelIndex
                    
        # lock it
        for item in items:
            if not item.path in self._lockedItems and not item.path in invalidPaths:
                self._lockedItems.append(item.path)
                result = self._findEffectedRowIntervals(item)
                self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
                for path, length in result:
                    index = self.indexFromPath(path)
                    if length > 0:
                        self.beginRemoveRows(index, 0, length - 1)
                        self.endRemoveRows()
                    if path in self._lockedItems:
                        self.beginInsertRows(index, 0, 0)
                        self.endInsertRows()
                self.emit(QtCore.SIGNAL("layoutChanged()"))
            
    def _findEffectedRowIntervals(self, item, result=None):
        """ Determines the already retrieved children of the given item. """
        
        if result is None:
            result = list()
        if item.childrenPopulated and item.isCollection:
            children = item.getChildren()
            for child in children:
                self._findEffectedRowIntervals(child, result)
            childrenLength = len(children)
            result.append((item.path, childrenLength))
        return result
    
    def unlock(self, index):
        """ Unlocks the given index. """
        
        item = self.nodeFromIndex(index)
        if item.path in self._lockedItems:
            result = self._findEffectedRowIntervals(item)
            result.reverse()
            self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
            self._lockedItems.remove(item.path)
            for path, length in result:
                if not path is None:
                    index = self.indexFromPath(path)
                    currentRowCount = self.rowCount(index)
                    if length > currentRowCount:
                        self.beginInsertRows(index, currentRowCount + 1, length)
                        self.endInsertRows()
                    elif length < currentRowCount:
                        self.beginRemoveRows(index, 0, currentRowCount - length - 1)
                        self.endRemoveRows()
            self.emit(QtCore.SIGNAL("layoutChanged()"))
            
    def clear(self):
        """ Cleans up everything and clears the model indexes. """

        self._repository.release()
        self._repository = None
        HistoryModel.clear(self)
        self.reset()
        self._actionHandler.clipboard.clear()
        self._lockedItems = list()
        
    def index(self, row, column, parent):
        """ L{index<PyQt4.QtCore.QAbstractItemModel.index>} """

        index = self._emptyQModelIndex
        item = self.nodeFromIndex(parent)
        if not item is None:
            try:
                if self._childrenPopulator.childrenPopulated(item):
                    child = item.getChildren()[row]
                    if not child.isCreated or item.path in self._lockedItems:
                        if child.isCollection:
                            child = self._placeHolderCollection
                        else:
                            child = self._placeHolderLeaf
                    index = self.createIndex(row, column, child)
                elif row == 0:
                    index = self.createIndex(row, column, self._placeHolderCollection)
            except IndexError:
                index = self._emptyQModelIndex
        return index

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """ L{headerData<PyQt4.QtCore.QAbstractItemModel.headerData>} """
        
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return QtCore.QVariant(self._headers[section])
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.QVariant(int(QtCore.Qt.AlignLeft))
        return self._emptyQVariant

    def data(self, index, role=0):
        """ L{data<PyQt4.QtCore.QAbstractItemModel.data>} """
        
        data = self._emptyQVariant
        item = _Item(self.nodeFromIndex(index))
        
        if role == 0: # QtCore.Qt.DisplayRole
            data = self._determineDisplayRole(index.column(), item)
        elif role == 1: # QtCore.Qt.DecorationRole
            data = self._determineDecoratorRole(index.column(), item)
        elif role == 3: # QtCore.Qt.ToolTipRole
            data = self._determineToolTipRole(index.column(), item)
        return data

    def _determineDisplayRole(self, column, item):
        """ Determines value of the different columns which has to be displayed. """
        
        data = self._emptyQVariant
        value = getattr(item, self._headerIds[column])
        if not value is None:
            if item.isLink and self._headerIds[column] == "name":
                if sys.platform == "win32" and item.uri.startswith("file:///") and value.endswith(".lnk"):
                    value = value[:-4]
            data = QtCore.QVariant(determineDisplayRepresentation(value, self._headerIds[column]))
        return data

    def _determineDecoratorRole(self, column, item):
        """ Determines icon associated with the specific item. """
        
        data = self._emptyQVariant
        if column == 0:
            if item.item != self._placeHolderCollection and item.item != self._placeHolderLeaf:
                if item.isLink and not item.linkTargetPath is None:
                    linkTargetIndex = self.indexFromPath(item.linkTargetPath)
                    if linkTargetIndex == self._emptyQModelIndex:
                        item.item._linkTarget = None
                    else:
                        item.item._linkTarget = self.nodeFromIndex(linkTargetIndex)
                data = QtCore.QVariant(self._iconProvider.iconForItem(item))
        return data

    def _determineToolTipRole(self, column, item):
        """ Determines the tool tip displayed for the specific item. """
        
        data = self._emptyQVariant
        if column == 0:
            if item.state in [ITEM_STATE_MIGRATED, ITEM_STATE_UNSUPPORTED_STORAGE_INTERFACE]:
                data = QtCore.QVariant("Data is currently not accessible.")
            elif item.state in [ITEM_STATE_ARCHIVED, ITEM_STATE_ARCHIVED_MEMBER, ITEM_STATE_ARCHIVED_READONLY]:
                data = QtCore.QVariant("Data is archived.")
            elif item.state in [ITEM_STATE_INACCESSIBLE]:
                data = QtCore.QVariant("Data is managed by an external inaccessible storage system.")
            elif item.isLink:
                if item.linkTargetPath is None:
                    data = QtCore.QVariant("No link target information available.")
                else:
                    data = QtCore.QVariant("Link Target: " + item.linkTargetPath)
            else:
                data = QtCore.QVariant(item.path)
        else:
            try:
                property_ = item.properties[self._headerIds[column]]
            except KeyError:
                data = self._emptyQVariant
            else:
                data = QtCore.QVariant(determinePropertyDefinitionToolTip(property_.propertyDefinition))  
        return data
    
    def hasChildren(self, index):
        """ L{hasChildren<PyQt4.QtCore.QAbstractItemModel.hasChildren>} """
        
        item = self.nodeFromIndex(index)
        if item is None:
            return False
        else:
            return item.isCollection

    def columnCount(self, _):
        """ L{columnCount<PyQt4.QtCore.QAbstractItemModel.columnCount>} """

        return len(self._headers)

    def rowCount(self, index):
        """ L{rowCount<PyQt4.QtCore.QAbstractItemModel.rowCount>} """

        rowCount = 0
        item = self.nodeFromIndex(index)
        if not item is None and item.isCollection:
            if item.path in self._lockedItems:
                rowCount = 1
            elif self._childrenPopulator.childrenPopulated(item): # only when children are populated the real row count is calculated
                rowCount = len(item.getChildren())
            else:
                rowCount = 1
        return rowCount
    
    def canFetchMore(self, index):
        """ 
        @see: L{canFetchMore<PyQt4.QtCore.QAbstractItemModel.canFetchMore>}

        @note: This method effectively populates child items.
        The items are only populated when the parent item is expanded.
        This behavior has been implemented to avoid expensive rowCount calls by Qt tree views
        which are determining the row count of the expanded item and all its children.
        """

        item = self.nodeFromIndex(index)
        if not item is None:
            if not self._childrenPopulator.childrenPopulated(item) \
               and not self._childrenPopulator.isWorkingOn(item):
                return True
        return False    

    def fetchMore(self, index):
        """ @see: L{fetchMore<PyQt4.QtCore.QAbstractItemModel.fetchMore>} """
        
        item = self.nodeFromIndex(index)
        if not item is None:
            self._childrenPopulator.populateChildren(item)
    
    def parent(self, index):
        """ @see: L{parentIndex<PyQt4.QtCore.QAbstractItemModel.parentIndex>} """

        parentIndex = self._emptyQModelIndex
        item = self.nodeFromIndex(index)
        try:
            parentItem = item.parent
        except (AttributeError, ItemError):
            parentItem = None
        if not parentItem is None:
            if not parentItem.parent is None:
                parentIndex = self._index(parentItem.path)
        return parentIndex

    def flags(self, index):
        """ L{flags<PyQt4.QtCore.QAbstractItemModel.flags>} """
        
        item = self.nodeFromIndex(index)
        if item == self._placeHolderCollection or item == self._placeHolderLeaf:
            return QtCore.Qt.NoItemFlags
        flags = QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsEnabled
        if index.column() == 0:
            if not (item.name.endswith(":") and sys.platform == "win32"):
                flags |= QtCore.Qt.ItemIsEditable
        return flags

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        """ L{sort<PyQt4.QtCore.QAbstractItemModel.sort>} """

        self._sortedColumn = column
        self._sortedOrder = order
        parent = self.nodeFromIndex(self.activeIndex)
        if self._childrenPopulator.childrenPopulated(parent):
            self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
            self.sortItems(parent.getChildren(), column, order)
            self.emit(QtCore.SIGNAL("layoutChanged()"))
        else:
            self._childrenPopulator.populateChildren(parent, callback=self._createSortCallback(parent, column, order))
        
    def _createSortCallback(self, parent, column, order):
        """ Creates a sort call back function. """
        def _sortCallback():
            """ Performs sorting. """

            children = parent.getChildren()
            self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
            self.sortItems(children, column, order)
            self.emit(QtCore.SIGNAL("layoutChanged()"))
            self.activeIndex = self.activeIndex
        return _sortCallback
    
    def sortItems(self, items, column, order):
        """ Sorts the given set of item. """

        if self.initialized:
            items.sort(reverse=order==QtCore.Qt.DescendingOrder, 
                       cmp=self._createCompareItemProperties(column))
            
    def _createCompareItemProperties(self, column):
        """ Creates the comparison function for the given column. """
        
        def _compareItemProperties(x, y):
            """ Performs the comparison. """
            
            propertyValueX = getattr(_Item(x), self._headerIds[column])
            propertyValueY = getattr(_Item(y), self._headerIds[column])
            
            if isinstance(propertyValueX, StringTypes) \
               and isinstance(propertyValueY, StringTypes):
                return cmp(propertyValueX.lower(), propertyValueY.lower())
            else:
                return cmp(propertyValueX, propertyValueY)
        return _compareItemProperties
    
    def nodeFromIndex(self, index):
        """
        Returns the node under the given index.

        @param index: The index of  the node that has to be returned.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        
        @return: The item for the given index.
        @rtype: L{BaseItem<datafinder.core.items.base.BaseItem>}
        """
        
        item = index.internalPointer()
        if item is None:
            if self.initialized:
                return self._repository.root
            else:
                return None
        return item
            
    def nodeFromPath(self, path):
        """
        Returns the node under the given path.

        @param path: The path of node that has to be returned.
        @type path: C{unicode}

        @return: The item of the given path.
        @rtype: L{BaseItem<datafinder.core.items.base.BaseItem>}
        """

        index = self._index(unicode(path))
        return self.nodeFromIndex(index)

    def indexFromPath(self, path, column=0):
        """
        Returns the index for the given path. 
        When the path does not exist the root index is returned.
        
        @param path: Path identifying the item.
        @type path: C{unicode}
        
        @return: Index referring to the item.
        @rtype: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        return self._index(path, column)

    def _index(self, path, column=0):
        """
        Converts a given path in the associated C{QtCore.QModelIndex}.
        
        @param path: Path that that has to be converted.
        @type path: C{unicode}
        @param column: Specifies the column of the returned index.
        @type column: C{int}
        
        @return: Associated index of the path.
        @rtype: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        path = path.replace("\\", "/")
        if not path.startswith("/"):
            path = "/" + path
        if path.endswith("/") and len(path) > 1:
            path = path[:-1]
        return self._find(path, self._emptyQModelIndex, column)
        
    def _find(self, path, parentIndex, column=0):      
        """      
        Traverse down the tree. Starts at the parent item.
        The token parameter contains a list that represents a path.
        When the path  was correct the underlying C{QtCore.QModelIndex}
        will returned else the default C{QtCore.QModelIndex}.
        
        @param path: Absolute path of the item.
        @type path: C{unicode}
        @param parentIndex: Parent item which marks the search start.
        @type parentIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        
        @return: Returns the index for the given token string.
        @rtype: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        index = self._emptyQModelIndex
        if not path is None and path != "/":
            parent = self.nodeFromIndex(parentIndex)
            if not parent is None:
                if not self._childrenPopulator.childrenPopulated(parent):
                    self._childrenPopulator.populateChildren(parent, True)
                children = parent.getChildren()
                for row, child in enumerate(children):
                    childIndex = self.createIndex(row, column, child)
                    if not child.path is None:
                        if path.lower() == child.path.lower():
                            return childIndex
                        if path[:len(child.path) + 1].lower() == child.path.lower() + "/":
                            return self._find(path, childIndex, column)
                    else:
                        print "Invalid child found '%s', '%s'." % (parent.path, child.name)
        return index
    
    @property
    def initialized(self):
        """ Initialized flag. """
        
        initialized = False
        if not self._repository is None:
            initialized = True
        return initialized
    
    @property
    def repository(self):
        """ Returns the underlying repository instance. """
        
        return self._repository
    
    @property
    def preferences(self):
        """ Returns the global preferences instance. """
        
        return self._preferences
    
    @property
    def iconProvider(self):
        """ Return the icon provider of the repository. """
        
        return self._iconProvider
    
    def __getattr__(self, name):
        """ Delegates to the action handler. """
        
        if self.initialized:
            return getattr(self._actionHandler, name)


class _ChildrenPopulator(object):
    """ Helper class allowing synchronous and asynchronous retrieval of item children. """
    
    def __init__(self, repositoryModel):
        """ Constructor. """
        
        self._repositoryModel = repositoryModel
        self._workerThreads = dict()
        self._logger = getDefaultLogger()
        
    def childrenPopulated(self, item):
        """
        Determines whether the children of the item are already retrieved.
        
        @param item: Item whose children should be populated.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        
        @return: C{True} when the children are currently retrieved.
        @rtype: C{bool}
        """
        
        childrenPopulated = False
        if item.childrenPopulated and not item.path in self._workerThreads:
            childrenPopulated = True
        return childrenPopulated
    
    def isWorkingOn(self, item):
        """
        Determines whether the children of the item are currently retrieved.
        
        @param item: Item whose children should be populated.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        
        @return: C{True} when the children are currently retrieved.
        @rtype: C{bool}
        """
        
        return item.path in self._workerThreads
        
    def populateChildren(self, item, synchronous=False, callback=None):
        """
        Populates the children of the given item asynchronously.
        
        @param item: Item whose children should be populated.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        @param synchronous: Flag determining whether the call is synchronously or not. 
        @type synchronous: C{bool}
        @param callback: Call back function that is called when populating children is done asynchronously.
        @type callback: C{function}
        """

        if not self.childrenPopulated(item) and not self.isWorkingOn(item):
            if synchronous:
                self._workerThreads[item.path] = ""
                try:
                    item.getChildren()
                except ItemError, error:
                    self._logger.error(error.message)

            callbacks = [self._createPopulateCallback(item), callback]
            self._workerThreads[item.path] = startNewQtThread(item.getChildren, callbacks)
    
    def _createPopulateCallback(self, item):
        """ Create a call back function for the specific item. """
        def _populateCallback():
            """ 
            This is the call back function for the corresponding 
            thread querying the children of a specific item.
            """
            
            if not item.path is None:
                try:
                    numberOfItems = len(item.getChildren())
                except ItemError:
                    numberOfItems = 0
                index = self._repositoryModel.indexFromPath(item.path)
                del self._workerThreads[item.path]
                currentRowCount = self._repositoryModel.rowCount(index)
                self._repositoryModel.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
                if numberOfItems > currentRowCount:
                    self._repositoryModel.beginInsertRows(index, currentRowCount + 1, numberOfItems)
                    self._repositoryModel.endInsertRows()
                elif numberOfItems < currentRowCount:
                    self._repositoryModel.beginRemoveRows(index, 0, currentRowCount - numberOfItems - 1)
                    self._repositoryModel.endRemoveRows()
                self._repositoryModel.emit(QtCore.SIGNAL("layoutChanged()"))
        return _populateCallback


class _Item(object):
    """ Helper class allowing access to item properties."""

    def __init__(self, item):
        """
        Constructor. 
        
        @param item: Item to wrap.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self._item = item
        
    def __getattr__(self, name):
        """ Overwrites the default attribute behavior. """
        
        if hasattr(self._item, name):
            return getattr(self._item, name)
        else:
            try:
                prop = self._item.properties[name]
                return prop.value
            except (KeyError, TypeError, AttributeError):
                return None

    @property
    def iconName(self):
        """ Getter for the icon name. """
        
        iconName = None
        source = self._item
        if self.isLink and not self.linkTarget is None:
            source = self.linkTarget
        if not source.dataType is None:
            iconName = source.dataType.iconName
        if not source.dataFormat is None:
            iconName = source.dataFormat.iconName
        return iconName

    @property
    def item(self):
        """ Getter for the encapsulated item. """
        
        return self._item
