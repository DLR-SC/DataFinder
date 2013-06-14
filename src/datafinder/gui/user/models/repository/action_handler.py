# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:
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
Implements actions of the data repository.
"""


import sys
        
from datafinder.core.configuration.properties.constants import UNMANAGED_SYSTEM_PROPERTY_CATEGORY, MANAGED_SYSTEM_PROPERTY_CATEGORY
from datafinder.core.error import ItemError, PropertyError
from datafinder.gui.user.common.util import StartInQtThread
from datafinder.gui.user.common.fileaction_handler import FileActionHandler
from datafinder.gui.user.models.repository.clipboard import ItemClipboard

    
__version__ = "$Revision-Id:$" 


class ActionHandler(object):
    """
    Implements actions of the data repository.
    """

    def __init__(self, parentModel, repository):
        """
        Constructor.
        
        @param parentModel: The repository model.
        @type parentModel: L{RepositoryModel<datafinder.gui.user.models.repository.RepsitoryModel>}
        @param repository: The underlying repository instance.
        @type repository: L{Repository<datafinder.core.repository.Repository>}
        """
        
        self._parentModel = parentModel
        self._repository = repository
        self._searchResult = list()
        self._itemClipboard = ItemClipboard(self._parentModel)
        self._fileActionHandler = None
        
        if not FileActionHandler is None:
            self._fileActionHandler = FileActionHandler()
            
    def refresh(self, index, itemStateOnly=False):
        """ 
        Refreshes the given item referred to as C{index}. 
        
        @param index: Index identifying the underlying item.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param itemStateOnly: If set it indicates that only the item 
                              state is refreshed but no structural information. Default is C{False}
        @type itemStateOnly: C{bool}
        """
        
        node = self._parentModel.nodeFromIndex(index)
        if not itemStateOnly:
            self._parentModel.lock([index])

        node.refresh(itemStateOnly)
        
        if not itemStateOnly:
            self._parentModel.unlock(index)
            self._parentModel.activeIndex = index
    
    def delete(self, indexes, ignoreStorageLocation=False):
        """ 
        Deletes the items referred to as C{indexes}. 
        
        @param index: Indexes identifying the items.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param ignoreStorageLocation: Optional flag indicating whether the storage location
                                      in case of managed repository items is ignored or not. Default: C{False}
        @type ignoreStorageLocation: C{bool}
        
        @raise ItemError: Indicating problems on deletion.
        """

        for index in indexes:
            if index.isValid():
                item = self._parentModel.nodeFromIndex(index)
                item.delete(ignoreStorageLocation)
                del item
    
    def copy(self, sourceIndexes, targetParentIndex):
        """ 
        Copies the item referenced by C{sourceIndex} under the item referenced 
        by C{targetParentIndex}.
        
        @param sourceIndexes: List of Indexes identifying the source items.
        @type sourceIndexes: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param targetParentIndex: Index identifying the parent item of the source item copies.
        @type targetParentIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        
        @raise ItemError: Indicating problems on copying.
        """
        
        for sourceIndex in sourceIndexes:
            if sourceIndex.isValid():
                sourceItem = self._parentModel.nodeFromIndex(sourceIndex)
                targetParentItem = self._parentModel.nodeFromIndex(targetParentIndex)
                targetName = self._repository.determineUniqueItemName(sourceItem.name, targetParentItem)
                targetItem = self._createNewItem(
                    targetName, targetParentItem, sourceItem.isCollection, 
                    sourceItem.linkTarget, sourceItem.isLink)
                try:
                    sourceItem.copy(targetItem)
                except ItemError, error:
                    targetItem.invalidate()
                    raise error

    def _createNewItem(self, name, parent, isCollection=False, 
                       linkTargetItem=None, isLink=False):
        """ Item factory helper method. """
        
        if isCollection:
            item = self._repository.createCollection(name, parent)
        elif isLink:
            item = self._repository.createLink(name, linkTargetItem, parent)
        else:
            item = self._repository.createLeaf(name, parent)
        return item

    def move(self, sourceIndexes, targetParentIndex, newName=None):
        """ 
        Moves the item referenced by C{sourceIndex} under the 
        item referenced by C{targetParentIndex}.
        
        @param sourceIndex: List of indexes identifying the source items.
        @type sourceIndex: C{list} of L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param targetParentIndex: Index identifying the new parent item of the source item.
        @type targetParentIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param newName: Optional new of the moved item.
        @type newName: C{unicode}
        
        @raise ItemError: Indicating problems on moving.
        """ 

        for sourceIndex in sourceIndexes:
            if sourceIndex.isValid():
                sourceItem = self._parentModel.nodeFromIndex(sourceIndex)
                targetParentItem = self._parentModel.nodeFromIndex(targetParentIndex)
                if targetParentItem.path.startswith(sourceItem.path):
                    postPath = targetParentItem.path[len(sourceItem.path):]
                    if len(postPath) == 0 or postPath[0] == "/":
                        raise ItemError("Cannot move item in its own sub-structure.")
                targetName = self._repository.determineUniqueItemName(newName or sourceItem.name, targetParentItem)
                try:
                    targetItem = self._createNewItem(
                        targetName, targetParentItem, sourceItem.isCollection, 
                        sourceItem.linkTarget, sourceItem.isLink)
                    sourceItem.move(targetItem)
                except ItemError, error:
                    targetItem.invalidate()
                    raise error
                else:
                    del sourceItem
    
    @StartInQtThread()    
    def updateProperties(self, index, changedProperties, deletablePropertyIds):
        """ 
        Updates the properties of the item referenced by C{index}. 
        
        @param index: Index identifying the source item.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param changedProperties: List of properties to add or update.
        @type changedProperties: C{list} of L{Property<datafinder.core.item.property.Property>}
        @param deletablePropertyIds: List of property identifier to remove.
        @type deletablePropertyIds: C{list} of C{unicode}
        """
        
        if index.isValid():
            item = self._parentModel.nodeFromIndex(index)
            if len(changedProperties) > 0 or len(deletablePropertyIds) > 0:
                item.updateProperties(changedProperties)
                item.deleteProperties(deletablePropertyIds)
                self._parentModel.itemDataChangedSignal(index)
            
    def copyProperties(self, sourceIndex, targetIndex):
        """
        Copies the properties of item referenced by C{sourceIndex} 
        to the item referenced by C{targetIndex}. Only data model or
        individual properties are copied. 
        
        @param sourceIndex: Index identifying the source item.
        @type sourceIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param targetIndex: Index identifying the target item.
        @type targetIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        if sourceIndex.isValid() and targetIndex.isValid():
            sourceItem = self._parentModel.nodeFromIndex(sourceIndex)
            targetItem = self._parentModel.nodeFromIndex(targetIndex)
            properties = list()
            for property_ in sourceItem.properties.values():
                if not property_.propertyDefinition.category \
                    in [UNMANAGED_SYSTEM_PROPERTY_CATEGORY, MANAGED_SYSTEM_PROPERTY_CATEGORY]:
                    properties.append(property_)
            targetItem.updateProperties(properties)
            self._parentModel.itemDataChangedSignal(targetIndex)

    def search(self, index, restrictions):
        """
        Performs a search request at the given collections with the given restrictions.

        @param index: Index identifying the collection that is searched.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param restrictions: A string specifying the restrictions.
        @type restrictions: C{unicode}
        
        @raise CoreError: Indicating problems on search.
        """

        collection = self._parentModel.nodeFromIndex(index)
        searchResult = self._repository.search(restrictions, collection)
        self._parentModel.searchResultChangedSignal(searchResult)

    def createCollection(self, name, parentIndex, properties=None):
        """ 
        Creates the collection with the given properties. 
        
        @param name: Name of the new collection.
        @type name: C{unicode}
        @param parentIndex: Index identifying the parent item of the new collection.
        @type parentIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param properties: Optional additional properties.
        @type properties: C{list} of L{Property<datafinder.core.item.property.Property>}
        
        @raise ItemError: Indicating problems on creation.
        """
        
        if properties is None:
            properties = list()
        parentItem = self._parentModel.nodeFromIndex(parentIndex)
        collection = self._createNewItem(name, parentItem, True)
        try:
            collection.create(properties)
        except (PropertyError, ItemError), error:
            collection.invalidate()
            raise error

    def createLeaf(self, name, parentIndex, properties, fileObject=None):
        """ 
        Creates the leaf. 
        
        @param name: Name of the new leaf.
        @type name: C{unicode}
        @param parentIndex: Index identifying the parent item of the new collection.
        @type parentIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param properties: Optional additional properties.
        @type properties: C{list} of L{Property<datafinder.core.item.property.Property>}
        
        @raise ItemError: Indicating problems on creation.
        """
        
        parentItem = self._parentModel.nodeFromIndex(parentIndex)
        leaf = self._createNewItem(name, parentItem)
        try:
            leaf.create(properties)
        except ItemError, error:
            leaf.invalidate()
            raise error
        else:
            if not fileObject is None:
                leaf.storeData(fileObject)

    def createLink(self, name, parentIndex, targetIndex, properties=None):
        """ 
        Creates the link. 
        
        @param name: Name of the new link.
        @type name: C{unicode}
        @param parentIndex: Index identifying the parent item of the new collection.
        @type parentIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param targetIndex: Identifies the item the link should point to.
        @type targetIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        
        @raise ItemError: Indicating problems on creation.
        """
        
        parentItem = self._parentModel.nodeFromIndex(parentIndex)
        targetItem = self._parentModel.nodeFromIndex(targetIndex)
        
        if sys.platform == "win32" and not name.endswith(".lnk") and parentItem.uri.startswith("file:///"):
            name += ".lnk"
        name = self._repository.determineUniqueItemName(name, parentItem)
        link = self._createNewItem(name, parentItem, linkTargetItem=targetItem, isLink=True)
        if properties is None:
            properties = list()
        
        try:
            link.create(properties)
        except ItemError, error:
            link.invalidate()
            raise error
 
    def createArchive(self, sourceIndex, targetParentIndex, properties=None):
        """
        Create an archive.

        @param sourceIndex: Index identifying the item which should be archived.
        @type sourceIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        @param targetParentIndex: Identifies the the parent of the new archive.
        @type targetParentIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        sourceParentItem = self._parentModel.nodeFromIndex(sourceIndex)
        targetParentItem = self._parentModel.nodeFromIndex(targetParentIndex)

        self._repository.createArchive(sourceParentItem, targetParentItem, properties)

    def isValidIdentifier(self, identifier):
        """ 
        Checks whether the given string describes a valid identifier.
        
        @param identifier: String describing the identifier.
        @type identifier: C{unicode}
        
        @return: C{True},C{None} if it is valid, otherwise C{False}, position
        @rtype: C{tuple} of C{bool}, C{int}
        """
        
        return self._repository.isValidIdentifier(identifier)
        
    def isValidPropertyIdentifier(self, identifier):
        """ 
        Checks whether the given string describes a valid property identifier.
        
        @param identifier: String describing the property identifier.
        @type identifier: C{unicode}
        
        @return: C{True} if it is valid, otherwise C{False}
        @rtype: C{bool}
        """
        
        return self._repository.isValidPropertyIdentifier(identifier)

    def performImport(self, sourceIndexes, targetParentIndex, defaultProperties=None):
        """
        Imports the given items potentially belonging to another 
        data repository below the given item specified by C{targetParentIndex}.
        
        @raise ItemError: Indicates problems on import.
        """
        
        targetParentItem = self._parentModel.nodeFromIndex(targetParentIndex)
        if defaultProperties is None:
            defaultProperties = list()
        
        failedItems = list()
        for sourceIndex in sourceIndexes:
            if sourceIndex.isValid():
                sourceItem = sourceIndex.model().nodeFromIndex(sourceIndex)
                targetItemName = self._repository.determineUniqueItemName(sourceItem.name, targetParentItem)
                try:
                    self._repository.performImport(sourceItem, targetParentItem, 
                                                   targetItemName, defaultProperties[:])  
                except ItemError, error:
                    failedItems.append((sourceItem, error.message))
        if len(failedItems) > 0:
            errorMessage = "Problems during import of the following items:\n"
            for item, message in failedItems:
                errorMessage += "\n" + item.path + " Reason: " + message
            raise ItemError(errorMessage)
            
    def performOpen(self, index):
        """
        Starts an external viewer for the given item identified by C{index}.
        
        @param index: Index identifying the parent item of the new collection.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        self._fileActionHandler.performOpen(self._parentModel.nodeFromIndex(index))

    def performPrint(self, index):
        """
        Prints the given item identified by C{index}.
        
        @param index: Index identifying the parent item of the new collection.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        self._fileActionHandler.performPrint(self._parentModel.nodeFromIndex(index))
            
            
    def commitArchive(self, indexes):
        """
        Commits changes of the given archives.
        
        @param indexes: Indexes of archives which should be committed.
        @type indexes: C{list} of L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        for index in indexes:
            if index.isValid():
                item = self._parentModel.nodeFromIndex(index)
                self._repository.commitArchive(item)
                
    def searchPrincipal(self, pattern, searchMode):
        """ 
        Just redirects to the repository functionality.
        @see: L{searchPrincipal<datafinder.core.repository.Repository.searchPrincipal>}
        """
        
        return self._repository.searchPrincipal(pattern, searchMode)
    
    @property
    def hasMetadataSearchSupport(self):
        """ Flag indicating support for meta data search. """
        
        return self._repository.hasMetadataSearchSupport
    
    @property
    def hasCustomMetadataSupport(self):
        """ Flag indicating support for meta data search. """
        
        return self._repository.hasCustomMetadataSupport

    @property
    def isManagedRepository(self):
        """ Flag indicating whether the repository is managed or not. """
        
        return self._repository.configuration.isManagedRepository

    @property
    def clipboard(self):
        """ 
        Getter for the item clip-board.
         
        @return: The item clip-board.
        @rtype: L{ItemClipboard<datafinder.gui.user.models.clipboard.ItemClipboard>}
        """
        
        return self._itemClipboard
