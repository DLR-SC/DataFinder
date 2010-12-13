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
from datafinder.core.configuration.properties.property_type import determinePropertyTypeConstant
from datafinder.gui.gen.user.list_property_dialog_ui import Ui_listPropertyDialog
from datafinder.gui.user.common.util import extractPyObject, determineDisplayRepresentation


__version__ = "$Revision-Id:$" 


class ListEditor(QtGui.QLineEdit):
    """
    This widget widget is a specialized line editor which allows 
    the manipulation of list data.
    """
    
    def __init__(self, editorFactory, initData=list(), parent=None):
        """
        Constructor.

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
        self._propertyTypeNames = [constants.STRING_TYPE, constants.DATETIME_TYPE, 
                                   constants.NUMBER_TYPE, constants.BOOLEAN_TYPE]
        
        self._editButton = QtGui.QPushButton("...", self)
        self._editButton.setMaximumSize(QtCore.QSize(20, 20))
        
        self.setReadOnly(True)
        self.setStyleSheet("QLineEdit { padding-right: 0px; } ")
        self.setText(determineDisplayRepresentation(initData))
        
        self._showEditorSlot()
        
        self.connect(self._editButton, QtCore.SIGNAL("clicked()"), self._showEditorSlot)
        
    def resizeEvent(self, _):
        """ Ensures that the edit button is in the right corner of the line editor. """
        
        size = self._editButton.maximumSize()
        self._editButton.move(self.rect().right() - size.width(),
                             (self.rect().bottom() + 1 - size.height()) / 2)

        
    def _showEditorSlot(self):
        """ Slot which shows the list editor. """
        
        listPropertyEditor = _ListPropertyDialog(self._propertyTypeNames, self.value, self._editorFactory, self)
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
    
    def __init__(self, propertyTypeNames, initData, editorFactory, parent=None):
        """
        Constructor.

        @param propertyTypeNames: Names of available property types.
        @type propertyTypeNames: C{list} of C{unicode}
        @param initData: Initial list data.
        @type initData: C{list} of C{object}
        @param editorFactory: Factory for creation of value editors.
        @type editorFactory: L{EditorFactory<datafinder.gui.user.common.widget.property.editors.factory.Editorfactory>}
        @param parent: Parent widget of the dialog.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget}
        """
        
        QtGui.QDialog.__init__(self, parent)
        Ui_listPropertyDialog.__init__(self)
        self.setupUi(self)
        
        self._initState = initData
        
        self.tableWidget.setItemDelegate(_ListPropertyItemDelegate(propertyTypeNames, editorFactory, self))
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accepted)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.rejected)
        self.connect(self.addButton, QtCore.SIGNAL("clicked()"), self.addSlot)
        self.connect(self.editButton, QtCore.SIGNAL("clicked()"), self.editSlot)
        self.connect(self.deleteButton, QtCore.SIGNAL("clicked()"), self.deleteSlot)
        self.tableWidget.setColumnWidth(1, 150)
        self._fillModelFromList(initData)
    
    def _fillModelFromList(self, propList):
        """
        Fills the model with items.
        
        @param propList: Content of the list property. Values are described in terms of the value and type constant.
        @type propList: C{list} of C{object}
        """
        
        for i, value in enumerate(propList):
            self.tableWidget.insertRow(i)
            self.tableWidget.setRowHeight(i, 20)
        
            try:
                typeConstant = determinePropertyTypeConstant(value)
            except ValueError:
                typeConstant = constants.STRING_TYPE
            self.tableWidget.setItem(i, 0 , QtGui.QTableWidgetItem(typeConstant))
            valueItem = _TableWidgetItem(value)
            self.tableWidget.setItem(i, 1, valueItem)
        
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
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
    
    def __init__(self, value=None):
        """
        Constructor. 
        
        @param value: Value which is represented by this item.
        @type value: C{object}
        """
        
        QtGui.QTableWidgetItem.__init__(self)
        self._value = value
    
    def _getValue(self):
        """ Getter of the value. """
        
        return self._value
    value = property(_getValue)
        
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
