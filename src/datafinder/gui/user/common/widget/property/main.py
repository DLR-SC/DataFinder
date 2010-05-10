#
# Created: 14.11.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: main.py 4479 2010-03-02 21:55:09Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the main part of the property widget.
"""


from PyQt4 import QtGui, QtCore

from datafinder.core.configuration.properties import constants
from datafinder.gui.user.common.widget.property.editors.factory import EditorFactory
from datafinder.gui.user.models.properties import PropertiesModel
from datafinder.gui.gen.widgets.property_widget_ui import Ui_propertyWidget


__version__ = "$LastChangedRevision: 4479 $"


class PropertyWidget(QtGui.QWidget, Ui_propertyWidget):
    """ Implements the main part of the property widget. """

    def __init__(self, parent):
        """ @see: L{QWidget<PyQt4.QtGui.QWidget>} """
        
        QtGui.QWidget.__init__(self, parent)
        Ui_propertyWidget.__init__(self)
        
        self.setupUi(self)
        self._model = None
        
        self.connect(self.addButton, QtCore.SIGNAL("clicked()"), self._addClickedSlot)
        self.connect(self.editButton, QtCore.SIGNAL("clicked()"), self._editClickedSlot)
        self.connect(self.clearValueButton, QtCore.SIGNAL("clicked()"), self._clearValueClickedSlot)
        self.connect(self.deleteButton, QtCore.SIGNAL("clicked()"), self._deleteClickedSlot)
        self.connect(self.revertButton, QtCore.SIGNAL("clicked()"), self._revertClickedSlot)
        self.connect(self.refreshButton, QtCore.SIGNAL("clicked()"), self._refreshClickedSlot)
        
    def _propertyStateChangedSlot(self):
        """ 
        Handles changes of properties of the model and updates
        the button enabled states in accordance to the selected entry.
        """
        
        index = self.propertiesTableView.selectionModel().currentIndex()
        self._updateButtonStates(index)
        
    def _updateSlot(self, index):
        """ 
        Slot is called when data of property entry has changed. 
        
        @param index: The index of the selected index.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        if index.isValid():
            self.propertiesTableView.selectionModel().setCurrentIndex(index, QtGui.QItemSelectionModel.ClearAndSelect)

    def _selectionChangedSlot(self, selected):
        """
        Slot is called when the selected property entry has changed.

        @param selected: The index of the selected property entry.
        @type selected: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        indexes = selected.indexes()
        if len(indexes) > 0:
            index = indexes[0]
            self._updateButtonStates(index)
            
    def _updateButtonStates(self, index):
        """ 
        Updates the state of the add, edit and delete button
        in accordance to the property state. 
        
        @param index: The index of the selected index.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        if index.isValid() and not self._model.isReadOnly:
            self.addButton.setEnabled(True)
            self.editButton.setEnabled(self._model.flags(index) & QtCore.Qt.ItemIsEditable)
            self.clearValueButton.setEnabled(self._model.canBeCleared(index))
            self.deleteButton.setEnabled(self._model.isDeleteable(index))
            self.revertButton.setEnabled(self._model.isRevertable(index))
        else:
            self._setInitialButtonState()
            
    def _setInitialButtonState(self):
        """ Sets the initial button state. """
        
        self.addButton.setEnabled(not self._model.isReadOnly)
        self.editButton.setEnabled(False)
        self.clearValueButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.revertButton.setEnabled(False)

    def _addClickedSlot(self):
        """ Slot is called when the add button is used. """

        index = self._model.add()
        self.propertiesTableView.selectionModel().setCurrentIndex(index, QtGui.QItemSelectionModel.ClearAndSelect)
        self._editClickedSlot()
        
    def _editClickedSlot(self):
        """ Slot is called when the edit button is used. """

        index = self.propertiesTableView.selectionModel().currentIndex()
        if index.isValid():
            self.propertiesTableView.edit(index)

    def _clearValueClickedSlot(self):
        """ Slot is called when the set empty button is used. """

        index = self.propertiesTableView.selectionModel().currentIndex()
        if index.isValid():
            self._model.clearValue(index)

    def _deleteClickedSlot(self):
        """ Slot is called when the delete button is used. """

        index = self.propertiesTableView.selectionModel().currentIndex()
        self._model.remove(index)

    def _revertClickedSlot(self):
        """ Slot is called when the revert button is used. """

        index = self.propertiesTableView.selectionModel().currentIndex()
        self._model.revert(index)

    def _refreshClickedSlot(self):
        """ Slot is called when the refresh button is used. """

        if self._model.dirty:
            button = QtGui.QMessageBox.information(self, self.tr("Refresh information"),
                                                   self.tr("All changes will be lost after the update.\n Do you want to continue?"),
                                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                                   QtGui.QMessageBox.Yes)
            if button == QtGui.QMessageBox.No:
                return
        self._model.refresh()
        self.propertiesTableView.setSortingEnabled(True)

    def _setModel(self, model):
        """ 
        Sets the model. 
        
        @param model: Model representing a set of properties.
        @type model: L{PropertiesModel<datafinder.gui.user.models.properties.PropertiesModel>}
        """
    
        self._model = model
        self.propertiesTableView.setModel(model)
        self._setInitialButtonState()
        
        column, order = self._model.sortProperties
        self.propertiesTableView.horizontalHeader().setSortIndicator(column, order)
        self.propertiesTableView.setSortingEnabled(True)
        propertyTypeNames = [constants.STRING_TYPE, constants.DATETIME_TYPE, 
                             constants.NUMBER_TYPE, constants.BOOLEAN_TYPE, constants.LIST_TYPE]
        self.propertiesTableView.setItemDelegate(_PropertyItemDelegate(propertyTypeNames, model, self))

        self.connect(self._model, QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self._updateSlot)
        self.connect(self.propertiesTableView.selectionModel(),
                     QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
                     self._selectionChangedSlot)
        self.connect(self._model, QtCore.SIGNAL(PropertiesModel.PROPERTY_STATE_CHANGED_SIGNAL), 
                     self._propertyStateChangedSlot)
        
    def _getModel(self):
        """ Getter of the property model. """
        
        return self._model
    
    def activateRefreshButton(self):
        """ Activates the refresh button. """
        
        self.refreshButton.show()
    
    def deactivateRefreshButton(self):
        """ De-activates the refresh button. """
        
        self.refreshButton.hide()
    
    model = property(_getModel, _setModel)
    

class _PropertyItemDelegate(QtGui.QStyledItemDelegate):
    """
    This item delegate has to choose the right editor for the expected property type
    and has to handle the conversion of the editor input to a proper model format.
    """

    def __init__(self, propertyTypes, model, parent=None):
        """
        Constructor.

        @param propertyTypes: Property types available for this property
        @type propertyTypes: C{list} of C{unicode}
        @param parent: Parent object of the delegate.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """

        QtGui.QStyledItemDelegate.__init__(self, parent)
        self._factory = EditorFactory()
        self._propertyTypes = propertyTypes
        self.connect(self, QtCore.SIGNAL("closeEditor(QWidget *, QAbstractItemDelegate::EndEditHint)"), self._handleEditorClosedSlot    )
        self._currentEditedRow = -1
        self._currentEditedColumn = -1
        self._model = model
        
    def _handleEditorClosedSlot(self, _, hint):
        """ Handles the closing of editor to remove added property entries without property name. """
        
        if hint == QtGui.QAbstractItemDelegate.RevertModelCache \
           and self._currentEditedColumn == 0:
            index = self._model.index(self._currentEditedRow, self._currentEditedColumn)
            index.model().setData(index, QtCore.QVariant(None))

    def createEditor(self, parent, _, index):
        """ @see: L{createEditor<PyQt4.QtGui.QItemDelegate.createEditor>} """

        self._currentEditedRow = index.row()
        self._currentEditedColumn = index.column()
        if index.column() == 0:
            editor = QtGui.QLineEdit(parent)
            editor.setValidator(_PropertyNameValidator(index.model().propertyNameValidationFunction, editor))
        elif index.column() == 1:
            editor = QtGui.QComboBox(parent)
            editor.addItems(self._propertyTypes)
            valueType = index.model().getModelData(index.row(), 1)
            if valueType in self._propertyTypes:
                editor.setCurrentIndex(self._propertyTypes.index(valueType))
        elif index.column() == 2:
            propType = index.model().getModelData(index.row(), 1)
            restriction = index.model().getModelData(index.row(), 4)
            pyValue = index.model().getModelData(index.row(), 2)
            editor = self._factory.createEditor(parent, propType, restriction, pyValue)
        return editor

    def setModelData(self, editor, model, index):
        """  @see: L{setModelData<PyQt4.QtGui.QItemDelegate.setModelData>} """
        
        value = self._factory.getValueFromEditor(editor)
        if type(value) == list:
            variantList = list()
            for item in value:
                variantList.append(QtCore.QVariant(item))
            variant = QtCore.QVariant.fromList(variantList)
        else:
            variant = QtCore.QVariant(value)
        model.setData(index, variant)
        
    def setEditorData(self, editor, index):
        """ L{setEditorData<PyQt4.QtGui.QItemDelegate.setEditorData>} """
        
        pyData = index.model().getModelData(index.row(), index.column())
        self._factory.setEditorValue(editor, pyData)


class _PropertyNameValidator(QtGui.QValidator):
    """ Custom validator for property name checking. """
    
    def __init__(self, validationFunction, parent=None):
        """
        Constructor. 
        
        @param validationFunction: Callable function which gets the property name as input and validates it.
        @type validationFunction: Callable C{object}
        """
        
        QtGui.QValidator.__init__(self, parent)
        self._validationFunction = validationFunction

    def validate(self, inputString, position):
        """ Overwrites the default implementation. """
        
        result = QtGui.QValidator.Invalid
        if self._validationFunction(unicode(inputString)) or len(inputString) == 0:
            result = QtGui.QValidator.Acceptable
        return (result, position)
