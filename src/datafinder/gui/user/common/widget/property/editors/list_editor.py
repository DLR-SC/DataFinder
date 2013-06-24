#
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
Dialog for editing list property values.
"""


from PyQt4 import QtGui, QtCore
from PyQt4.Qt import Qt

from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties import property_type
from datafinder.gui.gen.user.list_property_dialog_ui import Ui_listPropertyDialog
from datafinder.gui.user.common.util import extractPyObject, determineDisplayRepresentation


__version__ = "$Revision-Id:$" 


class ListEditor(QtGui.QLineEdit):
    """
    This widget widget is a specialized line editor which allows 
    the manipulation of list data.
    """
    
    
    _SUPPORTED_PROPERTY_TYPES = [
        constants.STRING_TYPE, constants.DATETIME_TYPE, constants.NUMBER_TYPE, constants.BOOLEAN_TYPE]
    
    
    def __init__(self, restrictions, editorFactory, initData=list(), parent=None):
        """
        
        @param restrictions: List-specific restrictions. 
            see: L{<property_type.ListType>datafinder.core.configuration.properties.property_type.ListType}
        @type restrictions: C{dict}
        @param editorFactory: Factory for creation of value editors.
        @type editorFactory: C{EditorFactory}
        @param initData: Initial list data.
        @type initData: C{list} of C{object}
        @param parent: Parent widget of the dialog.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget}
        """

        QtGui.QLineEdit.__init__(self, parent)
        
        self._editorFactory = editorFactory
        self.value = initData
        self._allowedPropertyTypes = restrictions.get(constants.ALLOWED_SUB_TYPES, self._SUPPORTED_PROPERTY_TYPES)
        self._removeUnsupportedPropertyTypes()
        
        self._editButton = QtGui.QPushButton("...", self)
        self._editButton.setMaximumSize(QtCore.QSize(20, 20))
        
        self.setReadOnly(True)
        self.setStyleSheet("QLineEdit { padding-right: 0px; } ")
        self.setText(determineDisplayRepresentation(initData))
        
        self._showEditorSlot()
        
        self.connect(self._editButton, QtCore.SIGNAL("clicked()"), self._showEditorSlot)
        
    def _removeUnsupportedPropertyTypes(self):
        removes = list()
        for propertyTypeName in self._allowedPropertyTypes:
            if not propertyTypeName in self._SUPPORTED_PROPERTY_TYPES:
                removes.append(propertyTypeName)
        for propertyTypeName in removes:
            self._allowedPropertyTypes.remove(propertyTypeName)
        
    def resizeEvent(self, _):
        """ Ensures that the edit button is in the right corner of the line editor. """
        
        size = self._editButton.maximumSize()
        self._editButton.move(self.rect().right() - size.width(),
                             (self.rect().bottom() + 1 - size.height()) / 2)

        
    def _showEditorSlot(self):
        """ Slot which shows the list editor. """
        
        listPropertyEditor = _ListPropertyDialog(self._allowedPropertyTypes, self.value, self._editorFactory, self)
        listPropertyEditor.exec_()
        self.setText(determineDisplayRepresentation(self.value))
        self.setFocus(Qt.OtherFocusReason)
        
    def text(self):
        """ Overwrites the text behavior. """
        
        return self.value


class _ListPropertyDialog(QtGui.QDialog, Ui_listPropertyDialog):
    """
    This dialog shows the content of a list property and supports the editing the property.
    """
    
    def __init__(self, allowedPropertyTypes, propertyValues, editorFactory, parent=None):
        """
        Constructor.

        @param allowedPropertyTypes: Names of available property types.
        @type allowedPropertyTypes: C{list} of C{unicode}
        @param propertyValues: Initial list data.
        @type propertyValues: C{list} of C{object}
        @param editorFactory: Factory for creation of value editors.
        @type editorFactory: L{EditorFactory<datafinder.gui.user.common.widget.property.editors.factory.Editorfactory>}
        @param parent: Parent widget of the dialog.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget}
        """
        
        QtGui.QDialog.__init__(self, parent)
        Ui_listPropertyDialog.__init__(self)
        self.setupUi(self)
        
        self._initState = propertyValues
        self._allowedPropertyTypes = allowedPropertyTypes
        self._editorFactory = editorFactory
        
        self._initializeSignalConnections()
        self._initializeEditButtonsEnabledState()
        self._initializeTable(propertyValues)
        
    def _initializeSignalConnections(self):
        self.connect(self.tableWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.itemSelectionChangedSlot)
        
        self.connect(self.addButton, QtCore.SIGNAL("clicked()"), self.addSlot)
        self.connect(self.editButton, QtCore.SIGNAL("clicked()"), self.editSlot)
        self.connect(self.deleteButton, QtCore.SIGNAL("clicked()"), self.deleteSlot)
        
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accepted)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.rejected)
        
    def _initializeEditButtonsEnabledState(self):
        if not self._allowedPropertyTypes:
            self.addButton.setEnabled(False)
        self._setEnableStateOfItemEditingButtons(False)
    
    def _setEnableStateOfItemEditingButtons(self, isEnabled):
        self.deleteButton.setEnabled(isEnabled)
        self.editButton.setEnabled(isEnabled)
        
    def _initializeTable(self, propertyValues):
        """
        Adds the property values into the table model.
        
        @param propertyValues: Property values which should be displayed in the editor.
        @type propertyValues: C{list} of C{object}
        """
        
        self.tableWidget.setItemDelegate(
            _ListPropertyItemDelegate(self._allowedPropertyTypes, self._editorFactory, self))
        self.tableWidget.setColumnWidth(1, 150)

        for row, value in enumerate(propertyValues):
            propertyType = property_type.determinePropertyTypeConstant(value)
            isEditingSupported = self._isEditingSupported(propertyType)
            self._addPropertyItem(row, value, propertyType, isEditingSupported)
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
    def _isEditingSupported(self, propertyType):
        if propertyType in self._allowedPropertyTypes:
            return True
        else:
            return False
        
    def _addPropertyItem(self, row, value, propertyType, isEditingSupported):
        self.tableWidget.insertRow(row)
        self.tableWidget.setRowHeight(row, 20)
        
        self.tableWidget.setItem(row, 0 , QtGui.QTableWidgetItem(propertyType))
        self.tableWidget.setItem(row, 1, _TableWidgetItem(value, isEditingSupported))

    def addSlot(self):
        """ This slot is called when a new item should be inserted. """
        
        self.tableWidget.insertRow(self.tableWidget.model().rowCount())
        self.tableWidget.setRowHeight(self.tableWidget.model().rowCount() - 1, 20)
        self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0,  QtGui.QTableWidgetItem(""))
        self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1,  _TableWidgetItem())
        self.tableWidget.setFocus()
        self.tableWidget.editItem(self.tableWidget.item(self.tableWidget.rowCount() - 1, 0))
                
    def editSlot(self):
        """ This slot is called when the edit button is pressed. """

        item = self.tableWidget.currentItem()
        self.tableWidget.editItem(item)

    def deleteSlot(self):
        """ Slot is called when the delete button is pressed. """
        
        index = self.tableWidget.selectionModel().currentIndex()
        self.tableWidget.model().removeRow(index.row())
        if self.tableWidget.rowCount() == 0:
            self._setEnableStateOfItemEditingButtons(False)
        
    def itemSelectionChangedSlot(self):
        """ De-activates buttons for properties which cannot be properly edited. """
        
        if self.tableWidget.selectedItems():
            item = self.tableWidget.selectedItems()[0]
            if item.column() == 0: # Only items of the value column contain the editing information
                item = self.tableWidget.item(item.row(), 1)  
            if item.isEditingSupported:
                self._setEnableStateOfItemEditingButtons(True)
            else:
                self._setEnableStateOfItemEditingButtons(False)
                
    def accepted(self):
        """ This slot is called when the user clicks OK. It returns the edited list. """
        
        properties = list()
        for i in range(self.tableWidget.model().rowCount()):
            item = self.tableWidget.item(i, 1)
            if not item.value is None:
                properties.append(item.value)
        
        self.parent().value = properties
        QtGui.QDialog.accept(self)
        
    def rejected(self):
        """
        This slot is called when the user cancels the dialog. It returns the
        list that was passed to dialog as initData.
        """
        
        self.parent().value = self._initState
        QtGui.QDialog.reject(self)

                
class _ListPropertyItemDelegate(QtGui.QItemDelegate):
    """
    Delegate for the property modification.
    """

    def __init__(self, propertyTypeNames, editorFactory, parent=None):
        """
        Constructor.

        @param propertyTypeNames: Names of available property types.
        @type propertyTypeNames: C{list} of C{unicode}
        @param editorFactory: Factory for creation of value editors.
        @type editorFactory: L{EditorFactory<datafinder.gui.user.common.widget.property.editors.factory.Editorfactory>}
        @param parent: Parent widget of the dialog.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget}
        """

        QtGui.QItemDelegate.__init__(self, parent)
        self._factory = editorFactory
        self._propertyTypes = [QtCore.QString(unicode(propType)) for propType in propertyTypeNames]

    def createEditor(self, parent, _, index):
        """
        @see: L{createEditor<PyQt4.QtGui.QItemDelegate.createEditor>}
        """

        typeIndex = index.model().index(index.row(), 0)
        valueType = index.model().data(typeIndex, QtCore.Qt.DisplayRole).toString()
        if index.column() == 0:
            editor = QtGui.QComboBox(parent)
            editor.addItems(self._propertyTypes)
            if valueType in self._propertyTypes:
                editor.setCurrentIndex(self._propertyTypes.index(valueType))
        elif index.column() == 1:
            editor = self._factory.createEditor(parent, valueType)
            if not editor.isEnabled():
                return None
        return editor

    def setModelData(self, editor, model, index):
        """
        @see: QtGui.QItemDelegate#setModelData
        """
        
        returnValue = self._factory.getValueFromEditor(editor)
        model.setData(index, QtCore.QVariant(returnValue))

    def setEditorData(self, editor, index):
        """
        @see: L{setEditorData<PyQt4.QtGui.QItemDelegate.setEditorData>}
        """
        
        if index.column() == 1:
            value = self.parent().tableWidget.item(index.row(), 1).value
            self._factory.setEditorValue(editor, value)
        else:
            QtGui.QItemDelegate.setEditorData(self, editor, index)


class _TableWidgetItem(QtGui.QTableWidgetItem):
    """ Specific implementation of C{QTableWidgetItem}. """
    
    def __init__(self, value=None, isEditingSupported=True):
        """
        @param value: Value which is represented by this item.
        @type value: C{object}
        @param isEditingSupported: Flag which indicates whether the value can be edited or not. 
        @type isEditingSupported: C{bool}
        """
        
        QtGui.QTableWidgetItem.__init__(self)
        self._value = value
        self._isEditingSupported = isEditingSupported
    
    @property
    def isEditingSupported(self):
        """ Read-only access to the isEditingSupported flag."""
        
        return self._isEditingSupported
    
    @property
    def value(self):
        """ Read-only access to the value."""
        
        return self._value
        
    def data(self, role):
        """ Ensures that the values are correctly rendered. """
        
        if role == Qt.DisplayRole:
            return QtCore.QVariant(determineDisplayRepresentation(self._value))
        else:
            return QtGui.QTableWidgetItem(self).data(role)
    
    def setData(self, _, value):
        """ Converts value given as QVariant to a Python object. """
        
        value = extractPyObject(value)
        self._value = value
