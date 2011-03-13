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
Provides the functionality of the add/edit data type dialog.
"""


from qt import QObject, SIGNAL, QPixmap, QIconSet, QMessageBox, QValidator, QStringList
from qttable import QTableItem, QCheckTableItem, QComboTableItem

from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration.properties.constants import DATAMODEL_PROPERTY_CATEGORY
from datafinder.core.error import ConfigurationError
from datafinder.gui.admin import icon_selection_dialog
from datafinder.gui.admin.common import utils
from datafinder.gui.gen.EditAddDataTypeDialog import AddEditDataTypeDialog


__version__ = "$Revision-Id:$" 


class ValidatedTableItem(QTableItem):
    """
    Table item with an additional validator for editor.
    It's using a
    L{DFPropertyValidator<datafinder.gui.Validators.DFPropertyValidator>}
    to validate that the input can be used as a property-name.

    @ivar validator: check property names
    @type validator: instance of C{PropertyValidator}
    """

    def __init__(self, table, row, column, txt, validationFunction):
        """
        Constructor.

        @param table: "parent" table
        @type table: L{QTable<qt.QTable>}
        @param txt: text
        @type txt: C{unicode}
        """

        QTableItem.__init__(self, table, QTableItem.Always, txt)
        self._table = table
        self._row = row
        self._column = column
        self.validator = None
        self._validationFunction = validationFunction

    def createEditor(self):
        """ Creates a (standard) QLineEdit and inits and adds validator. """

        editor = QTableItem.createEditor(self)
        self._table.connect(editor, SIGNAL("textChanged(const QString&)"), self._valueChangedSlot)
        self.validator = PropertyValidator(editor)
        self.validator.validationFunction = self._validationFunction
        editor.setValidator(self.validator)
        return editor
    
    def _valueChangedSlot(self, _):
        """ Signals the change of the specific cell. """
        
        self._table.emit(SIGNAL("valueChanged"), (self._row, self._column))


class PropertyValidator(QValidator):
    """
    Derived QValidator to check compliance of new property-names
    to DataFinder-specific rules (see L{datafinder.common.NameCheck}).
    
    Remark:
    =======
        Return-type of QValidator.validate() is a 
        tuple (QValidator.Invalid, cursor-position):
        U{http://www.mail-archive.com/pykde@mats.gmd.de/msg01830.html}
    """
    def __init__(self, *args):
        """ Constructor. """
        
        QValidator.__init__(self, *args)
        self.validationFunction = None
    
    def validate(self, inputStr, pos):
        """
        Check if string inputStr is a valid property-name.
        
        @return: L{qt.QValidator.Acceptable} or L{qt.QValidator.Invalid}
        """
        
        if self.validationFunction(unicode(inputStr)) or len(inputStr) == 0:
            return (self.Acceptable, pos)
        else:
            return (self.Invalid, pos)


class DataTypeView(AddEditDataTypeDialog):
    """
    This is the view component of the add/edit Data type dialog. The class
    is derived from the generated python class. The user input is delegated
    to the controller component.
    """

    def __init__(self, parentFrame, controller, propertyIdValidationFunction, propertyTypeNames):
        """
        Constructor.

        @param parentFrame: Reference to the parent frame.
        @type parentFrame: L{QWidget<qt.QWidget>}
        @param controller: Reference to the controller component.
        @type controller: L{DataTypeController}
        """

        AddEditDataTypeDialog.__init__(self, parentFrame)
        self.propertyTable.setColumnStretchable(3, True)
        self._controller = controller
        self._connectSignalsWithSlots()
        self._contentChanged = False
        self._propertyIdValidationFunction = propertyIdValidationFunction
        self._propertyTypeNames = propertyTypeNames

    def _connectSignalsWithSlots(self):
        """ Connects signals with the according slots. """

        self.connect(self.dataTypeNameLineEdit,
                     SIGNAL("textChanged(const QString&)"),
                     self._controller.changeTitleSlot)
        self.connect(self.dataTypeSelectIconPushButton,
                     SIGNAL("clicked()"),
                     self._controller.selectIconSlot)
        self.connect(self.propertyTable,
                     SIGNAL("valueChanged(int, int)"),
                     self._controller.propertyTableValueChangedSlot)
        self.connect(self.newAttributePushButton,
                     SIGNAL("clicked()"),
                     self._controller.newAttributeSlot)
        self.connect(self.removeAttributePushButton,
                     SIGNAL("clicked()"),
                     self._controller.removeAttributeSlot)
        self.connect(self.savePushButton,
                     SIGNAL("clicked()"),
                     self._controller.saveSlot)
        self.connect(self.resetPushButton,
                     SIGNAL("clicked()"),
                     self._controller.resetSlot)
        self.connect(self.cancelPushButton,
                     SIGNAL("clicked()"),
                     self._controller.closeDialogSlot)

    def updateDataType(self, title, iconName, propertyList):
        """
        Updates the displayed data type.

        @param title: Name of edited data type if existing, "New_DataType" otherwise (at the same time a title from this dialog).
        @type title: C{unicode}
        @param iconName: Name of data type icon.
        @type iconName: C{unicode}
        @param propertyList: List of properties.
        @type propertyList: C{list} of C{unicode}
        """

        self.dataTypeNameLineEdit.setText(title)
        self.setCaption(title)
        self.dataTypeIconLabel.setPixmap(utils.getPixmapForImageName(iconName, False))
        self.propertyTable.setNumRows(len(propertyList))
        rowIndex = 0
        propertyList.sort()
        for myProperty in propertyList:
            self._addAttribute(myProperty, rowIndex)
            rowIndex += 1
        for index in range(4):
            self.propertyTable.adjustColumn(index)

    def isContentChanged(self):
        """ Checks if the data type has changed. """

        return self._contentChanged

    def setButtonsState(self, enabled):
        """
        Sets the transitions state of the dialog.

        @param enabled: Indicates if the transition is enabled.
        @type enabled: C{boolean}
        """

        if len(self.myEditedTitle.strip()) == 0:
            self.savePushButton.setEnabled(False)
        else:
            self.savePushButton.setEnabled(enabled)
        self.resetPushButton.setEnabled(enabled)

        if len(self.myPropertyList) == 0:
            self.removeAttributePushButton.setEnabled(False)
        else:
            self.removeAttributePushButton.setEnabled(True)

        self._contentChanged = enabled

    def getNumberOfRowsWithBlankRow(self):
        """
        Creates a blank row for a new attribute.

        @return: number of rows, including the newly created blank row.
        @rtype: C{int}
        """

        self._endPendingEditOperations()
        numberOfRows = self.propertyTable.numRows()
        self.propertyTable.setNumRows(numberOfRows + 1)

        textTableItem = ValidatedTableItem(self.propertyTable, numberOfRows, 0, "", self._propertyIdValidationFunction)
        self.propertyTable.setItem(numberOfRows, 0, textTableItem)
        typeComboBox = self._getTypeCombobox()
        typeComboBox.setCurrentItem("Any")
        self.propertyTable.setItem(numberOfRows, 1, typeComboBox)
        self.propertyTable.setItem(numberOfRows, 3, QCheckTableItem(self.propertyTable, ""))
        return self.propertyTable.numRows()

    def _addAttribute(self, attribute, rowIndex):
        """
        Adds a predefined attribute.

        @param attribute: Attribute of this data type.
        @type attribute: L{PropertyDefinition<datafinder.application.PropertyDefinition.PropertyDefinition>}
        @param rowIndex: Row index.
        @type rowIndex: C{int}
        """

        textTableItem = ValidatedTableItem(self.propertyTable, rowIndex, 0, attribute.identifier, self._propertyIdValidationFunction)
        self.propertyTable.setItem(rowIndex, 0, textTableItem)
        typeComboBox = self._getTypeCombobox()
        typeComboBox.setCurrentItem(attribute.type or "Any")
        self.propertyTable.setItem(rowIndex, 1, typeComboBox)
        self.propertyTable.setText(rowIndex, 2, attribute.defaultValue or "")
        self.propertyTable.setItem(rowIndex, 3, QCheckTableItem(self.propertyTable, ""))
        self.propertyTable.item(rowIndex, 3).setChecked(attribute.notNull)

    def _getTypeCombobox(self):
        """ Initailizes and returns a combination box displaying available property types. """
        
        stringList = QStringList()
        for typeName in self._propertyTypeNames:
            stringList.append(typeName)
        typeComboBox = QComboTableItem(self.propertyTable, stringList)
        return typeComboBox
        
    def _getEditedTitle(self):
        """
        Returns a name of the displayed data type (at the same time a title from this dialog).

        @return: Name of the displayed data type.
        @rtype: C{unicode}
        """

        editedTitle = unicode(self.dataTypeNameLineEdit.text())
        return editedTitle

    def _getPropertyList(self):
        """ Returns a list of the currently displayed attributes. """

        self._endPendingEditOperations()
        propertyList = []
        for row in range(self.propertyTable.numRows()):
            if not self.propertyTable.text(row, 0).isEmpty():
                propertyName = unicode(self.propertyTable.text(row, 0))
                propertyType = unicode(self.propertyTable.text(row, 1))
                propertyDefault = unicode(self.propertyTable.text(row, 2))
                propertyMandatory = self.propertyTable.item(row, 3).isChecked()
                myProperty = (propertyName, propertyMandatory, propertyType, propertyDefault)
                propertyList.append(myProperty)
        return propertyList

    def _endPendingEditOperations(self):
        """ Ends all edit operations. """

        self.propertyTable.endEdit(self.propertyTable.currentRow(), self.propertyTable.currentColumn(), True, False)

    def _getSelectedRowList(self):
        """ Returns a list of the currently selected rows. """

        self._endPendingEditOperations()
        index = self.propertyTable.numRows() - 1
        selectedRowList = []
        # collect the indexes of selected rows in a list
        # must count backwards, because the rows are to be removed
        while index >= 0:
            if self.propertyTable.isRowSelected(index):
                selectedRowList = selectedRowList + [index]
            index = index - 1

        return selectedRowList

    myEditedTitle = property(_getEditedTitle)
    mySelectedRowList = property(_getSelectedRowList)
    myPropertyList = property(_getPropertyList)


class DataTypeController(object):
    """
    The controller component of the add/edit data type dialog. It controls the presentation
    and delegates signals of the view to the data model.
    """

    def __init__(self, parentFrame, title, repositoryConfiguration, existingDataType=True):
        """
        Constructor.

        @param parentFrame: Reference to the parent frame.
        @type parentFrame: L{QWidget<qt.QWidget>}
        @param title: Name of edited data type if existing, "New_DataType" otherwise (at the same time a title from this dialog).
        @type title: C{unicode}
        """

        self._parentFrame = parentFrame
        propertyTypeNames = repositoryConfiguration.propertyDefinitionFactory.PROPERTY_TYPE_NAMES[:]
        self._dataTypeView = DataTypeView(parentFrame, self, repositoryConfiguration.propertyNameValidationFunction, propertyTypeNames)
        self._dataTypeView.setModal(True)
        self._dataTypeModel = DataTypeModel(title, repositoryConfiguration.dataModelHandler, 
                                            repositoryConfiguration.propertyDefinitionFactory, repositoryConfiguration.iconHandler)
        self._dataTypeModel.initDataType()
        self.title = self._dataTypeModel.myTitle
        self._dataTypeView.updateDataType(self._dataTypeModel.myTitle, self._dataTypeModel.myIconName,
                                          self._dataTypeModel.myPropertyList)
        self._dataTypeView.setButtonsState(False)
        self._dataTypeView.savePushButton.setEnabled(not existingDataType)

        #open and specific formats not implemented:
        self._dataTypeView.dataTypeTabWidget.setTabEnabled(self._dataTypeView.tab_2, False)
        self._dataTypeView.dataTypeTabWidget.setTabEnabled(self._dataTypeView.tab_3, False)

    def _setNodeIcon(self):
        """ Sets the node icon. """

        pixmap = utils.getPixmapForImageName(self._dataTypeModel.myIconName)
        mask = QPixmap.fromMimeSource(u"newMask16.png")
        pixmap.setMask(mask.createHeuristicMask())
        icon = QIconSet(pixmap)
        self._parentFrame.changeIconPixmap(icon, self.title, self._dataTypeModel.myTitle)

    def changeTitleSlot(self):
        """ Sets the title (name of data type) from the line edit field. """

        self._dataTypeModel.myTitle = self._dataTypeView.myEditedTitle
        self._dataTypeView.setCaption(self._dataTypeView.myEditedTitle)
        self._dataTypeView.setButtonsState(True)

    def selectIconSlot(self):
        """ Selects a new icon for this data type. """

        selectIconDialog = icon_selection_dialog.SelectUserIconDialog()
        iconNames = selectIconDialog.getIconName(self._dataTypeModel.icons, self._dataTypeModel.myIconName)
        if len(iconNames) > 0:
            self._dataTypeModel.myIconName = iconNames[0]
            self._dataTypeView.dataTypeIconLabel.setPixmap(utils.getPixmapForImageName(iconNames[0], False))
            self._setNodeIcon()
            self._dataTypeView.setButtonsState(True)

    def newAttributeSlot(self):
        """ Slot to handle new attribute. """

        self._dataTypeView.getNumberOfRowsWithBlankRow()
        self._dataTypeView.setButtonsState(True)
        self._dataTypeView.removeAttributePushButton.setEnabled(True)

    def propertyTableValueChangedSlot(self):
        """ Slot to handle value changes. """

        self._dataTypeModel.myPropertyList = self._dataTypeView.myPropertyList
        self._dataTypeView.setButtonsState(True)

    def removeAttributeSlot(self):
        """ Removes selected rows/attributes. """

        if self._dataTypeView.propertyTable.currentSelection() == -1:
            QMessageBox.information(self._parentFrame, self._parentFrame.tr("DataFinder: No Selection"),
                                          "Please select a row to remove!",
                                          self._parentFrame.tr("OK"), "", "",
                                          0, -1)
        else:
            for index in self._dataTypeView.mySelectedRowList:
                self._dataTypeView.propertyTable.removeRow(index)
            self._dataTypeModel.myPropertyList = self._dataTypeView.myPropertyList
            self._dataTypeView.setButtonsState(True)

    def closeDialogSlot(self):
        """ Closes the dialog for the currently displayed data type. """

        if self._dataTypeView.isContentChanged():
            result = QMessageBox.warning(self._parentFrame, self._parentFrame.tr("DataFinder: Unsaved Changes"),
                                              "Save changes?", self._parentFrame.tr("Save"), self._parentFrame.tr("Discard"),
                                              self._parentFrame.tr("Cancel"), 0, 2)
            # Cancel or close of dialog by window handle
            if result == -1 or result == 2:
                #returnValue = False
                pass
            # Save
            elif result == 0:
                self.saveSlot()
            # Discard: close
            elif result == 1:
                self._dataTypeView.close()
        else:
            self._dataTypeView.close()

    def resetSlot(self):
        """ Resets the values of the currently displayed data type. """

        self._dataTypeModel.initDataType()
        self._dataTypeView.updateDataType(self._dataTypeModel.myTitle, self._dataTypeModel.myIconName, self._dataTypeModel.myPropertyList)
        self._setNodeIcon()
        self._dataTypeView.setButtonsState(False)

    def saveSlot(self):
        """ Saves the currently displayed data type. """

        self._dataTypeModel.myPropertyList = self._dataTypeView.myPropertyList
        try:
            self._dataTypeModel.saveDataType()
        except ConfigurationError, error:
            getDefaultLogger().error(error.message)
        else:
            self._dataTypeView.close()
            self._parentFrame.updateDataTypes()
            getDefaultLogger().info("Data Type " + self._dataTypeModel.myTitle + " was successfully saved.")

    def __getattr__(self, name):
        """ Delegates calls to the generated PyQt class. """

        return getattr(self._dataTypeView, name)


class DataTypeModel(QObject):
    """
    This is the data model of the add/edit data type dialog that contains the current
    data type or none and the list of available data types.
    """

    def __init__(self, title, dataModelHandler, propertyDefinitionFactory, iconHandler):
        """
        Constructor.

        @param title: Name of edited data type if existing, "New_DataType" otherwise (at the same time a title from this dialog).
        @type title: C{unicode}
        """

        QObject.__init__(self)
        self._dataModelHandler = dataModelHandler
        self._propertyDefinitionFactory = propertyDefinitionFactory
        self._iconHandler = iconHandler
        
        self.__dataType = self._dataModelHandler.createDataType(title)
        self.__title = title
        self.__referenceTitle = title
        self.__iconName = None
        self.__propertyList = None

    @property
    def icons(self):
        """ Icons getter. """
        
        return self._iconHandler.allIcons
    
    def initDataType(self):
        """ Initializes a data type (initial and by reset). """

        self.__dataType = self._dataModelHandler.getDataType(self.__referenceTitle)
        if self.__dataType is None:
            self.__dataType =  self._dataModelHandler.createDataType()
        self.__title = self.__dataType.name
        self.__iconName = self.__dataType.iconName
        self.__propertyList = self.__dataType.propertyDefinitions
        
    def saveDataType(self):
        """ Saves the currently displayed data type. """

        propertyDefinitions = self._getPropertyDefinitions()
        dataType = self._dataModelHandler.createDataType(iconName=self.__iconName, propertyDefinitions=propertyDefinitions)
        dataType.name = self.__title
        
        # add data type to configuration and store configuration
        self._dataModelHandler.addDataType(dataType)
        self._dataModelHandler.store()

        self.__referenceTitle = self.__title

    def _getPropertyDefinitions(self):
        """ Creates the property definition objects. """
        
        propertyDefinitions = list()
        for propertyName, isMandatory, propertyTypeName, defaultValue in self.__propertyList:
            propertyType = self._propertyDefinitionFactory.createPropertyType(propertyTypeName)
            propertyDefinition = self._propertyDefinitionFactory.createPropertyDefinition(propertyName, DATAMODEL_PROPERTY_CATEGORY, 
                                                                                          propertyType, namespace=self.__title)
            propertyDefinition.notNull = isMandatory
            if len(defaultValue) == 0:
                defaultValue = None
            propertyDefinition.defaultValue = defaultValue
            propertyDefinitions.append(propertyDefinition)
        return propertyDefinitions
        
    def _setPropertyList(self, propertyList):
        self.__propertyList = propertyList

    def _getPropertyList(self):
        return self.__propertyList

    def _setIconName(self, iconName):
        self.__iconName = iconName

    def _getIconName(self):
        return self.__iconName

    def _setTitle(self, title):
        self.__title = title

    def _getTitle(self):
        return self.__title

    myTitle = property(_getTitle, _setTitle)
    myIconName = property(_getIconName, _setIconName)
    myPropertyList = property(_getPropertyList, _setPropertyList)
