# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
#
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
This module contains the properties model.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.user.common.util import \
    extractPyObject, determineDisplayRepresentation, determinePropertyDefinitionToolTip
from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties.domain import DomainObject
from datafinder.core.configuration.properties.property_type import \
    determinePropertyTypeConstant, PROPERTY_TYPE_NAMES
from datafinder.core.error import PropertyError


__version__ = "$Revision-Id:$" 


class PropertiesModel(QtCore.QAbstractTableModel):
    """ This model represents a set of properties. """

    PROPERTY_STATE_CHANGED_SIGNAL = "propertyStateChanged"
    IS_CONSISTENT_SIGNAL = "isConsistentSignal"

    _SYSTEM = 1
    _DATA = 2
    _PROP = 4
    _NEW = 8
    _DELETED = 16
    _EDITED = 32
    _REQUIRED_NOT_SET = 64
    _DOMAIN_PROPERTY = 128 # Used until there is a complete editor
    
    def __init__(self, repositoryModel, trackRepositoryUpdates=True):
        """
        @param repositoryModel: The parent model which handles access to item of the data repository.
        @type repositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.RepositoryModel>}
        @param trackRepositoryUpdates: Optional flag determining whether the property model
                                       reacts on changes of the repository. Default: C{true}
        @type trackRepositoryUpdates: C{bool}
        """

        QtCore.QAbstractTableModel.__init__(self)

        self._sortedColumn = 0
        self._sortedOrder = QtCore.Qt.AscendingOrder
        self._headers = [self.tr("Name"), self.tr("Type"), self.tr("Value")]

        self._itemIndex = None
        self.isReadOnly = False
        self._isConsistent = False
        self.itemName = ""
        self._repositoryModel = repositoryModel
        self._properties = list(list())
        if trackRepositoryUpdates:
            self.connect(self._repositoryModel, QtCore.SIGNAL("itemDataChanged"), self._handleUpdateSlot)
            self.connect(self._repositoryModel, QtCore.SIGNAL("modelReset()"), self.clear)
    
    def _handleUpdateSlot(self, index):
        """ Updates properties if the displayed item changed . """
        
        try:
            if index.row() == self._itemIndex.row():
                self.itemIndex = index
                self.reset()
                self._emitPropertyDataChanged()
        except AttributeError:
            pass # Nothing to do, index has already been handled.
            
    def _emitPropertyDataChanged(self):
        """ Emits the signal C{self.PROPERTY_STATE_CHANGED_SIGNAL}. """
        
        self.emit(QtCore.SIGNAL(self.PROPERTY_STATE_CHANGED_SIGNAL))
    
    def load(self, properties):
        """
        Initializes the model with the given properties.
        
        @param properties: Properties represented by this model.
        @type properties: C{list} of L{Property<datafinder.core.item.property.Property>}
        """

        self._properties = list(list())
        propertyIds = list()
        for prop in properties:
            propDef = prop.propertyDefinition
            state = self._determinePropertyState(propDef.category)
            if not propDef.identifier in propertyIds and not state is None:
                propertyIds.append(propDef.identifier)
                value = prop.value
                    
                if (not propDef.type in PROPERTY_TYPE_NAMES
                    or isinstance(value, DomainObject)):
                    state |= self._DOMAIN_PROPERTY
                displayPropertyTypeName = self._determinePropertyTypeName(propDef.type, value)
                self._properties.append([propDef.displayName, displayPropertyTypeName, value,
                                         propDef, propDef.restrictions, propDef.type, value, state])
        self._checkConsistency()

    def _checkConsistency(self):
        """ Checks whether all properties are set correctly. """
        
        self._isConsistent = True
        for prop in self._properties:
            try:
                propDef = prop[3]
                if not propDef is None:
                    prop[3].validate(prop[2])
                if prop[-1] & self._REQUIRED_NOT_SET:
                    prop[-1] ^= self._REQUIRED_NOT_SET # Remove the "Not Set" flag
            except PropertyError:
                prop[-1] |= self._REQUIRED_NOT_SET
                self._isConsistent = False
        self.emit(QtCore.SIGNAL(self.IS_CONSISTENT_SIGNAL), self._isConsistent)

    @staticmethod
    def _determinePropertyState(category):
        """ Determines the internal state of the property. E.g. data model specific. """
        
        if category in (constants.UNMANAGED_SYSTEM_PROPERTY_CATEGORY, 
                        constants.MANAGED_SYSTEM_PROPERTY_CATEGORY):
            state = PropertiesModel._SYSTEM
        elif category == constants.DATAMODEL_PROPERTY_CATEGORY:
            state = PropertiesModel._DATA
        elif category == constants.USER_PROPERTY_CATEGORY:
            state = PropertiesModel._PROP
        else:
            state = None
        return state
        
    @staticmethod
    def _determinePropertyTypeName(propertyType, value):
        """ Determines the display name of the property type. """
        
        displayPropertyTypeName = propertyType
        if propertyType == constants.ANY_TYPE:
            if value is None:
                displayPropertyTypeName = constants.STRING_TYPE
            else:
                displayPropertyTypeName = determinePropertyTypeConstant(value)
                
        dotIndex = displayPropertyTypeName.rfind(".")
        if dotIndex > 0:
            startIndex = dotIndex + 1
            if not startIndex >= len(displayPropertyTypeName):
                displayPropertyTypeName = displayPropertyTypeName[startIndex:]
        return displayPropertyTypeName    
        
    def rowCount(self, _=QtCore.QModelIndex()):
        """ @see: L{rowCount<PyQt4.QtCore.QAbstractTableModel.rowCount>} """
        
        return len(self._properties)

    def columnCount(self, _):
        """ @see: L{columnCount<PyQt4.QtCore.QAbstractTableModel.columnCount>} """

        return len(self._headers)

    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        """ @see: L{headerData<PyQt4.QtCore.QAbstractTableModel.headerData>} """

        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self._headers[section])
            if role == QtCore.Qt.TextAlignmentRole:
                return QtCore.QVariant(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter))
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """ @see: L{data<PyQt4.QtCore.QAbstractTableModel.data>} """

        row = index.row()
        column = index.column()
        variant = QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            variant = self._getValueDisplayRepresentation(row, index)
        elif role == QtCore.Qt.BackgroundColorRole:
            state = self._properties[row][-1]
            attribute = QtGui.QColor(QtCore.Qt.white)
            if state & self._DELETED:
                attribute = QtGui.QColor(255, 100, 100)
            elif state & self._NEW:
                attribute = QtGui.QColor(100, 255, 100)
            elif state & self._REQUIRED_NOT_SET:
                attribute = QtGui.QColor(255, 255, 0)
            elif state & self._EDITED:
                attribute = QtGui.QColor(240, 240, 240)
            variant = QtCore.QVariant(attribute)
        elif role == QtCore.Qt.ToolTipRole:
            propertyEntry = self._properties[index.row()]
            if column == 0:
                if not propertyEntry[3] is None:
                    variant = determinePropertyDefinitionToolTip(propertyEntry[3])
            elif column == 2:
                variant = self._getValueDisplayRepresentation(row, index)
        return variant

    def _getValueDisplayRepresentation(self, row, index):
        value = self._properties[row][index.column()]
        if index.column() == 2:
            propDef = self._properties[row][3]
            propId = None
            if not propDef is None:
                propId = propDef.identifier
            variant = QtCore.QVariant(determineDisplayRepresentation(value, propId))
        else:
            variant = QtCore.QVariant(value)
        return variant
    
    def setData(self, index, value, _=None):
        """ @see: L{setData<PyQt4.QtCore.QAbstractTableModel.setData>} """

        row = index.row()
        column = index.column()

        value = extractPyObject(value)
        try:
            changed = cmp(self._properties[row][column], value)
        except TypeError:
            changed = True
        
        if changed:
            self._properties[row][column] = value
            if not self._properties[row][-1] & self._NEW:
                self._properties[row][-1] |= self._EDITED
                self._checkConsistency()
            if column == 1:
                self._properties[row][2] = None
                self._checkConsistency()

        if self._properties[row][0] is None:
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            del self._properties[row]
            self.endRemoveRows()
            self._emitPropertyDataChanged()
            return False

        self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)
        self._emitPropertyDataChanged()
        return True

    def flags(self, index):
        """ @see: L{flags<PyQt4.QtCore.QAbstractTableModel.flags>} """

        state = self._properties[index.row()][-1]
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        if not self.isReadOnly:
            if state & self._NEW \
               or (state & (self._DATA|self._PROP) and index.column() == 2) \
               or (self._properties[index.row()][5] == constants.ANY_TYPE and state & (self._DATA|self._PROP) and index.column() == 1):
                flags |= QtCore.Qt.ItemIsEnabled
                if (not state & self._DELETED
                    and not state & self._DOMAIN_PROPERTY):
                    flags |= QtCore.Qt.ItemIsEditable
        return flags

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        """ @see: L{sort<PyQt4.QtCore.QAbstractTableModel.sort>} """

        self._sortedColumn = column
        self._sortedOrder = order
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self._properties.sort(reverse = (order == QtCore.Qt.DescendingOrder),
                              cmp=lambda x, y: cmp(determineDisplayRepresentation(x[column]).lower(), 
                                                   determineDisplayRepresentation(y[column]).lower()))
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def save(self):
        """ Saves property modifications of the given item. """

        dirty = False
        for row in self._properties:
            state = row[-1]
            if state &  (self._EDITED|self._NEW| self._DELETED):
                dirty = True
        if dirty:
            self._updateProperties(self._properties)
        
    def _updateProperties(self, properties):
        """ Converts the data saved in the model back to its internally used 
        representation and stores it. """
        
        addedEditedProperties = list()
        deletableProperties = list()
        for prop in properties:
            state = prop[-1]
            if state & self._DELETED:
                deletableProperties.append(prop[0])
            elif state & self._NEW:
                newProperty = self._repositoryModel.repository.createProperty(prop[0], prop[2])
                addedEditedProperties.append(newProperty)
            elif state & self._EDITED:
                newProperty = self._repositoryModel.repository.createPropertyFromDefinition(prop[3], prop[2])
                addedEditedProperties.append(newProperty)
        if len(addedEditedProperties) > 0 or len(deletableProperties) > 0:
            if not self._itemIndex is None:
                self._repositoryModel.updateProperties(self._itemIndex, addedEditedProperties, deletableProperties)
                    
    def clear(self):
        """ Clears the model internal data and resets the model. """

        self._itemIndex = None
        self._properties = list()
        self.reset()

    def refresh(self):
        """ Reloads all data from the server and resets the data model. """

        if not self._itemIndex is None:
            self._repositoryModel.refresh(self._itemIndex, True)
            self.itemIndex = self._itemIndex
            self.sort(self._sortedColumn, self._sortedOrder)
            self.reset()
            self._emitPropertyDataChanged()

    def add(self):
        """
        Appends a "blank" property to the existing properties.

        @return: The index the new property.
        @rtype: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self._properties.append([None, None, None, None, None, constants.ANY_TYPE, None, self._NEW])
        self.endInsertRows()

        index = self.createIndex(row, 0, self._properties[row][0])
        self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)
        self._emitPropertyDataChanged()
        return index

    def clearValue(self, index):
        """ 
        Clears the value of the property, i.e. set it to C{None}.
        
        @param index: The index that has to be cleared.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self._properties[index.row()][2] = None
        self._properties[index.row()][-1] |= self._EDITED
        self._checkConsistency()
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)
        self._emitPropertyDataChanged()
        
    def remove(self, index):
        """
        iF the item is new it will be deleted instantly. Otherwise the property
        will be deleted after a save operation.

        @param index: The index that has to be removed.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        row = index.row()
        props = self._properties[row][-1]

        if not props & self._NEW | self._PROP:
            raise ValueError("Given index at %d, %d can not be deleted." % (row, index.column()))

        if props & self._NEW:
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            del self._properties[row]
            self.endRemoveRows()
        else:
            self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
            self._properties[row][-1] |= self._DELETED
            self.emit(QtCore.SIGNAL("layoutChanged()"))
            self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)
        self._emitPropertyDataChanged()
        
    def revert(self, index=None):
        """
        If the given index has the status deleted, this method removes the deleted status.

        @param index: The index that has to be reverted.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        if not index is None:
            row = index.row()
            self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
            if self._properties[row][-1] & self._DELETED:
                self._properties[row][-1] ^= self._DELETED
            elif self._properties[row][-1] & self._EDITED:
                originalValue = self._properties[row][6]
                originalType = self._determinePropertyTypeName(self._properties[row][5], originalValue)
                self._properties[row][1] = originalType
                self._properties[row][2] = originalValue
                self._properties[row][-1] ^= self._EDITED
                self._checkConsistency()
            self.emit(QtCore.SIGNAL("layoutChanged()"))
            self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)
            self._emitPropertyDataChanged()
            
    def _isPropertyNameUnique(self, propertyName):
        for item in self._properties:
            existingIdentifer = item[0]
            if not item[3] is None:
                existingIdentifer = item[3].identifier
            if existingIdentifer == propertyName:
                return False
        return True 
    
    def isDeleteable(self, index):
        """
        @param index: Index that has to be checked.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}

        @return: C{True} if the index can be deleted else C{False}.
        @rtype: C{bool}
        """

        state = self._properties[index.row()][-1]
        return (bool(state & (self._NEW | self._PROP)) 
                and not bool(state & self._DELETED))

    def isRevertable(self, index):
        """
        @param index: Index that has to be checked.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}

        @return: C{True} if the index can be reverted else c{False}.
        @rtype: C{bool}
        """

        state = self._properties[index.row()][-1]
        return (bool(state & (self._DELETED | self._EDITED)) 
                and not bool(state & self._NEW))

    def canBeCleared(self, index):
        """
        @param index: Index that has to be checked.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}

        @return: C{True} if the index can be cleared else C{False}.
        @rtype: C{bool}
        """

        state = self._properties[index.row()][-1]
        return (not bool(state & self._SYSTEM)
                and not bool(state & self._DOMAIN_PROPERTY)
                and not self._properties[index.row()][2] is None)

    def getModelData(self, row, column):
        """ This function allows direct access the model data structure. """
        
        return self._properties[row][column]
    
    @property
    def hasCustomMetadataSupport(self):
        return self._repositoryModel.hasCustomMetadataSupport

    @property
    def propertyNameValidationFunction(self):
        def wrapper(inputString):
            return self._repositoryModel.repository.configuration.propertyNameValidationFunction(inputString) \
                   and self._isPropertyNameUnique(inputString)
        return wrapper

    @property
    def dirty(self):
        """
        @return: C{True} if the data has changed else C{False}.
        @rtype: C{bool}
        """

        for item in self._properties:
            if item[-1] & (self._EDITED | self._DELETED | self._NEW):
                return True
        return False

    @property
    def sortProperties(self):
        """
        @return: The properties for the sorting, i.e. sorted column number and sort order.
        @rtype: C{tuple}
        """

        return self._sortedColumn, self._sortedOrder

    @property
    def properties(self):
        """
        @return: List of property instances contained in this model.
        @rtype: C{list} of L{Property<datafinder.core.item.property.Property>}
        """
        
        properties = list()
        for prop in self._properties:
            if prop[-1] & self._NEW:
                newProperty = self._repositoryModel.repository.createProperty(prop[0], prop[2])
            else:
                newProperty = self._repositoryModel.repository.createPropertyFromDefinition(prop[3], prop[2])
            properties.append(newProperty)
        return properties
             
    @property
    def isConsistent(self):
        """ Checks whether all properties are set correctly. """
        
        return self._isConsistent
             
    def _setItemIndex(self, index):
        """
        Set the index from which the properties have to be loaded.
        In the most cases this is the current selected index in the view.

        @param itemIndex: The itemIndex from which the properties has to be loaded.
        @type itemIndex: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        self._properties = list(list())
        self.isReadOnly = True
        if index.isValid():
            item = self._repositoryModel.nodeFromIndex(index)
            if item.isLink:
                item = item.linkTarget
            if not item is None:
                if not item.path is None:
                    self._itemIndex = self._repositoryModel.indexFromPath(item.path)
                    self.itemName = item.name
                    self.isReadOnly = not item.capabilities.canStoreProperties
                    properties = item.properties.values()
                    self.load(properties)
                    self.sort(self._sortedColumn, self._sortedOrder)
    itemIndex = property(fset=_setItemIndex)
