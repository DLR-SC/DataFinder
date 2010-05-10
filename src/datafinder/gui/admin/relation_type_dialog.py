#
# Created: 05.11.2007 Anastasia Eifer <Anastasia.Eifer@dlr.de>
# Changed: $Id: relation_type_dialog.py 4100 2009-05-24 18:12:19Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder/
#


"""
Provides the functionality of the add/edit relation type dialog.
"""


from qt import QObject, PYSIGNAL, SIGNAL, QPixmap, QIconSet, QMessageBox

from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration.datamodel.constants import ROOT_RELATION_NAME
from datafinder.core.error import ConfigurationError
from datafinder.gui.admin import icon_selection_dialog
from datafinder.gui.admin.common import utils
from datafinder.gui.gen.EditAddRelationTypeDialog import AddEditRelationTypeDialog


__version__ = "$LastChangedRevision: 4100 $"


# custom signals
relationTypeChanged = "relationTypeChanged"


class RelationTypeView(AddEditRelationTypeDialog):
    """
    This is the view component of the add/edit relation type dialog. The class
    is derived from the generated python class. The user input is delegated
    to the controller component. Changes of the data model are signaled with
    Qt signal/slot mechanism.
    """

    def __init__(self, parentFrame, controller):
        """
        Constructor.

        @param parentFrame: Reference to the parent frame.
        @type parentFrame: L{QWidget<qt.QWidget>}
        @param controller: Reference to the controller component.
        @type controller: L{RelationTypeController}
        """

        AddEditRelationTypeDialog.__init__(self, parentFrame)
        self._controller = controller
        self._connectSignalsWithSlots()
        self._contentChanged = False

    def _connectSignalsWithSlots(self):
        """ Connects signals with the according slots. """

        self.connect(self.relationTypeNameLineEdit,
                     SIGNAL("textChanged(const QString&)"),
                     self._controller.changeTitleSlot)
        self.connect(self.relationTypeSelectIconPushButton,
                     SIGNAL("clicked()"),
                     self._controller.selectIconSlot)
        self.connect(self.parentDataTypeAddPushButton,
                     SIGNAL("clicked()"),
                     self._controller.addParentDataTypesSlot)
        self.connect(self.parentDataTypeRemovePushButton,
                     SIGNAL("clicked()"),
                     self._controller.removeParentDataTypesSlot)
        self.connect(self.childDataTypeAddPushButton,
                     SIGNAL("clicked()"),
                     self._controller.addChildDataTypesSlot)
        self.connect(self.childDataTypeRemovePushButton,
                     SIGNAL("clicked()"),
                     self._controller.removeChildDataTypesSlot)
        self.connect(self.savePushButton,
                     SIGNAL("clicked()"),
                     self._controller.saveSlot)
        self.connect(self.resetPushButton,
                     SIGNAL("clicked()"),
                     self._controller.resetSlot)
        self.connect(self.cancelPushButton,
                     SIGNAL("clicked()"),
                     self._controller.closeDialogSlot)

    def updateRelationType(self, title, iconName, parentDataTypeList, childDataTypeList):
        """
        Updates the displayed relation type.

        @param title: Name of edited relation type if existing, "New_RelationType" otherwise (at the same time a title from this dialog).
        @type title: C{unicode}
        @param iconName: Name of relation type icon.
        @type iconName: C{unicode}
        @param parentDataTypeList: List of parent data types.
        @type parentDataTypeList: C{list} of C{unicode}
        @param childDataTypeList: List of parent data types.
        @type childDataTypeList: C{list} of C{unicode}
        """

        self.relationTypeNameLineEdit.setText(title)
        if title == ROOT_RELATION_NAME:
            self.relationTypeNameLineEdit.setEnabled(False)
        else:
            self.relationTypeNameLineEdit.setEnabled(True)
        self.setCaption(title)
        if not iconName is None:
            self.relationTypeIconLabel.setPixmap(utils.getPixmapForImageName(iconName, False))
        self.parentDataTypeListBox.clear()
        self.childDataTypeListBox.clear()
        parentDataTypeList.sort()
        childDataTypeList.sort()
        for parentDataTypeName in parentDataTypeList:
            self.parentDataTypeListBox.insertItem(parentDataTypeName, -1)
        for childDataTypeName in childDataTypeList:
            self.childDataTypeListBox.insertItem(childDataTypeName, -1)

    def isContentChanged(self):
        "Checks if the relation type has changed"""

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

        if self.parentDataTypeListBox.count() == 0:
            self.parentDataTypeRemovePushButton.setEnabled(False)
        else:
            self.parentDataTypeRemovePushButton.setEnabled(True)

        if self.childDataTypeListBox.count() == 0:
            self.childDataTypeRemovePushButton.setEnabled(False)
        else:
            self.childDataTypeRemovePushButton.setEnabled(True)

        if self.availableDataTypeListBox.count() == 0:
            self.parentDataTypeAddPushButton.setEnabled(False)
            self.childDataTypeAddPushButton.setEnabled(False)
        else:
            self.parentDataTypeAddPushButton.setEnabled(True)
            self.childDataTypeAddPushButton.setEnabled(True)

        self._contentChanged = enabled

    def _setAvailableDataTypeList(self, availableDataTypeList):
        """
        Shows a list of available data types.

        @param availableDataTypeList: List of available data types.
        @type availableDataTypeList: C{list} of L{DataTypes<datafinder.application.RelationType.RelationType>} elements.
        """
        for dataType in availableDataTypeList:
            self.availableDataTypeListBox.insertItem(dataType.name, -1)
        self.availableDataTypeListBox.sort()

    def _getAvailableDataTypeList(self):
        """
        Returns a list of available data types.

        @return: List of available data types.
        @rtype: C{list} of C{unicode}
        """
        return self.__availableDataTypeList

    def _getEditedTitle(self):
        """
        Returns a name of the displayed relation type (at the same time a title from this dialog).

        @return: Name of the displayed relation type.
        @rtype: C{unicode}
        """

        editedTitle = unicode(self.relationTypeNameLineEdit.text())
        return editedTitle

    def _getSelectedAvailableDataTypeList(self):
        """
        Returns a list of the currently selected available data types.

        @return: List of available data types.
        @rtype: C{list} of C{unicode}
        """

        selectedDataTypeList = []
        index = self.availableDataTypeListBox.count() - 1
        while index >= 0:
            if self.availableDataTypeListBox.isSelected(index):
                selectedDataType = unicode(self.availableDataTypeListBox.item(index).text())
                selectedDataTypeList.append(selectedDataType)
            index = index - 1
        return selectedDataTypeList

    def _getSelectedParentDataTypeList(self):
        """
        Returns a list of the currently selected parent data types

        @return: List of the currently selected parent data types.
        @rtype: C{list} of C{unicode}
        """

        selectedDataTypeList = []
        index = self.parentDataTypeListBox.count() - 1
        while index >= 0:
            if self.parentDataTypeListBox.isSelected(index):
                selectedDataType = unicode(self.parentDataTypeListBox.item(index).text())
                selectedDataTypeList.append(selectedDataType)
            index = index - 1
        return selectedDataTypeList

    def _getSelectedChildDataTypeList(self):
        """
        Returns a list of the currently selected child data types.

        @return: List of the currently selected child data types.
        @rtype: C{list} of C{unicode}
        """

        selectedDataTypeList = []
        index = self.childDataTypeListBox.count() - 1
        while index >= 0:
            if self.childDataTypeListBox.isSelected(index):
                selectedDataType = unicode(self.childDataTypeListBox.item(index).text())
                selectedDataTypeList.append(selectedDataType)
            index = index - 1
        return selectedDataTypeList

    myAvailableDataTypeList = property(_getAvailableDataTypeList, _setAvailableDataTypeList)
    myEditedTitle = property(_getEditedTitle)
    mySelectedAvailableDataTypeList = property(_getSelectedAvailableDataTypeList)
    mySelectedParentDataTypeList = property(_getSelectedParentDataTypeList)
    mySelectedChildDataTypeList = property(_getSelectedChildDataTypeList)


class RelationTypeController(object):
    """
    The controller component of the add/edit relation type dialog. It controls the presentation
    and delegates signals of the view to the data model.
    """

    def __init__(self, parentFrame, title, repositoryConfiguration, existingRelationType=True):
        """
        Constructor.

        @param parentFrame: Reference to the parent frame.
        @type parentFrame: L{QWidget<qt.QWidget>}
        @param repositoryConfiguration: The configuration of the repository.
        @type repositoryConfiguration: L{RepositoryConfiguration<datafinder.core.configuration.repository.RepositoryConfiguration>}
        @param title: Name of edited relation type if existing, "New_RelationType" otherwise (at the same time a title from this dialog).
        @type title: C{unicode}
        """

        self._parentFrame = parentFrame
        self._repositoryConfiguration = repositoryConfiguration

        self._relationTypeView = RelationTypeView(parentFrame, self)
        self._relationTypeView.setModal(True)
        self._relationTypeModel = RelationTypeModel(title, repositoryConfiguration.dataModelHandler, repositoryConfiguration.iconHandler)
        self._parentFrame.connect(self._relationTypeModel,
                                  PYSIGNAL(relationTypeChanged),
                                  self._relationTypeView.updateRelationType)
        self._relationTypeModel.initRelationType()
        self.title = self._relationTypeModel.myTitle
        self.initializeAvailableDataTypeList()
        self._relationTypeView.setButtonsState(False)
        self._relationTypeView.savePushButton.setEnabled(not existingRelationType)

    def _setNodeIcon(self):
        """ Sets the node icon """

        pixmap = utils.getPixmapForImageName(self._relationTypeModel.myIconName)
        mask = QPixmap.fromMimeSource(u"newMask16.png")
        pixmap.setMask(mask.createHeuristicMask())
        icon = QIconSet(pixmap)
        self._parentFrame.changeIconPixmap(icon, self.title, self._relationTypeModel.myTitle)

    def initializeAvailableDataTypeList(self):
        """ Initializes a list of available data types. """

        self._relationTypeView.myAvailableDataTypeList = self._relationTypeModel.myAvailableDataTypeList

    def changeTitleSlot(self):
        """ Sets the title (name of relation type) from the line edit field. """

        self._relationTypeModel.myTitle = self._relationTypeView.myEditedTitle
        self._relationTypeView.setButtonsState(True)

    def selectIconSlot(self):
        """ Selects a new icon for this relation type. """

        selectIconDialog = icon_selection_dialog.SelectUserIconDialog()
        iconNames = selectIconDialog.getIconName(self._repositoryConfiguration.iconHandler.allIcons, self._relationTypeModel.myIconName)
        if len(iconNames) > 0:
            self._relationTypeModel.myIconName = iconNames[0]
            self._relationTypeView.relationTypeIconLabel.setPixmap(utils.getPixmapForImageName(iconNames[0], False))
            self._setNodeIcon()
            self._relationTypeView.setButtonsState(True)

    def addParentDataTypesSlot(self):
        """ Adds the selected data types from the list of available data types to the list of parent data types. """

        if self._relationTypeView.mySelectedAvailableDataTypeList == []:
            QMessageBox.information(self._parentFrame, self._parentFrame.tr("DataFinder: No Selection"),
                                          "Please select a Data Type to add!",
                                          self._parentFrame.tr("OK"), "", "",
                                          0, -1)
        else:
            self._relationTypeModel.addParentDataTypes(self._relationTypeView.mySelectedAvailableDataTypeList)
            self._relationTypeView.setButtonsState(True)

    def removeParentDataTypesSlot(self):
        """ Removes the selected data type from the list of parent data types. """

        if self._relationTypeView.mySelectedParentDataTypeList == []:
            QMessageBox.information(self._parentFrame, self._parentFrame.tr("DataFinder: No Selection"),
                                          "Please select a Data Type to remove!",
                                          self._parentFrame.tr("OK"), "", "",
                                          0, -1)
        else:
            self._relationTypeModel.removeParentDataTypes(self._relationTypeView.mySelectedParentDataTypeList)
            self._relationTypeView.setButtonsState(True)

    def addChildDataTypesSlot(self):
        """ Adds the selected data types from the list of available data types to the list of child data types. """

        if self._relationTypeView.mySelectedAvailableDataTypeList == []:
            QMessageBox.information(self._parentFrame, self._parentFrame.tr("DataFinder: No Selection"),
                                          "Please select a Data Type to add!",
                                          self._parentFrame.tr("OK"), "", "",
                                          0, -1)
        else:
            self._relationTypeModel.addChildDataTypes(self._relationTypeView.mySelectedAvailableDataTypeList)
            self._relationTypeView.setButtonsState(True)

    def removeChildDataTypesSlot(self):
        """ Removes the selected data type from the list of parent data types. """

        if self._relationTypeView.mySelectedChildDataTypeList == []:
            QMessageBox.information(self._parentFrame, self._parentFrame.tr("DataFinder: No Selection"),
                                          "Please select a Data Type to remove!",
                                          self._parentFrame.tr("OK"), "", "",
                                          0, -1)
        else:
            self._relationTypeModel.removeChildDataTypes(self._relationTypeView.mySelectedChildDataTypeList)
            self._relationTypeView.setButtonsState(True)

    def closeDialogSlot(self):
        """ Closes the dialog for the currently displayed relation type. """

        if self._relationTypeView.isContentChanged():
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
                self._relationTypeView.close()
        else:
            self._relationTypeView.close()

    def resetSlot(self):
        """ Resets the values of the currently displayed relation type. """

        self._relationTypeModel.initRelationType()
        self._setNodeIcon()
        self._relationTypeView.setButtonsState(False)

    def saveSlot(self):
        """ Saves the currently displayed relation type. """

        self._relationTypeView.close()
        try:
            self._relationTypeModel.saveRelationType()
        except ConfigurationError, error:
            getDefaultLogger().error(error.message)
        else:
            self._parentFrame.updateRelationTypes()
            getDefaultLogger().info("Relation Type " + self._relationTypeModel.myTitle + " was successfully saved.")

    def __getattr__(self, name):
        """ Delegates calls to the generated PyQt class. """

        return getattr(self._relationTypeView, name)


class RelationTypeModel(QObject):
    """
    This is the data model of the add/edit relation type dialog that contains the current
    relation type or none and the list of available data types
    """

    def __init__(self, title, dataModelHandler, iconHandler):
        """
        Constructor.
        @param title: Name of edited relation type if existing, "New_RelationType" otherwise (at the same time a title from this dialog).
        @type title: C{unicode}
        """

        QObject.__init__(self)
        self._dataModelHandler = dataModelHandler
        self._iconHandler = iconHandler

        self.__relationType = self._dataModelHandler.createRelation(title)
        self.__title = title
        self.__referenceTitle = title
        self.__iconName = None
        self.__parentDataTypeList = None
        self.__childDataTypeList = None
        self.__availableDataTypeList = self._dataModelHandler.datatypes

    def initRelationType(self):
        """ Initializes a relation type. """

        self.__relationType = self._dataModelHandler.getRelation(self.__referenceTitle)
        if self.__relationType is None:
            self.__relationType = self._dataModelHandler.createRelation()
        self.__title = self.__relationType.name
        self.__iconName = self.__relationType.iconName
        self.__parentDataTypeList = self.__relationType.sourceDataTypeNames
        self.__childDataTypeList = self.__relationType.targetDataTypeNames
        self.__signalRelationTypeChanged()

    def addParentDataTypes(self, selectedAvailableDataTypeList):
        """
        Adds the selected data types from the list of available data types to the list of parent data types.
        @param selectedAvailableDataTypeList: List of selected available data types.
        @type selectedAvailableDataTypeList: C{list} of C{unicode}
        """

        for dataType in selectedAvailableDataTypeList:
            if not self.isElement(dataType, self.__parentDataTypeList):
                self.__parentDataTypeList.append(dataType)
        self.__signalRelationTypeChanged()

    def removeParentDataTypes(self, selectedParentDataTypeList):
        """
        Removes the selected data type from the list of parent data types.
        @param selectedParentDataTypeList: List of selected parent data types.
        @type selectedParentDataTypeList: C{list} of C{unicode}
        """

        for dataType in selectedParentDataTypeList:
            self.__parentDataTypeList.remove(dataType)
        self.__signalRelationTypeChanged()

    def addChildDataTypes(self, selectedAvailableDataTypeList):
        """
        Adds the selected data types from the list of available data types to the list of child data types.
        @param selectedAvailableDataTypeList: List of selected available data types.
        @type selectedAvailableDataTypeList: C{list} of C{unicode}
        """

        for dataType in selectedAvailableDataTypeList:
            if not self.isElement(dataType, self.__childDataTypeList):
                self.__childDataTypeList.append(dataType)
        self.__signalRelationTypeChanged()

    def removeChildDataTypes(self, selectedChildDataTypeList):
        """
        Removes the selected data type from the list of child data types.
        @param selectedChildDataTypeList: List of selected child data types.
        @type selectedChildDataTypeList: C{list} of C{unicode}
         """

        for dataType in selectedChildDataTypeList:
            self.__childDataTypeList.remove(dataType)
        self.__signalRelationTypeChanged()

    def saveRelationType(self):
        """ Saves the currently displayed relation type. """

        relation = self._dataModelHandler.createRelation(iconName=self.__iconName)
        relation.name = self.__title
        relation.sourceDataTypeNames = self.__parentDataTypeList
        relation.targetDataTypeNames = self.__childDataTypeList

        # add relation type to configuration and write configuration
        self._dataModelHandler.addRelation(relation)
        self._dataModelHandler.store()

        self.__referenceTitle = self.__title

    def isElement(dataType, dataTypeList):
        """
        Returns True, if this data type is an element of the list, False otherwise.
        @return: true/false
        @rtype: C{bool}
        """

        return dataTypeList.count(dataType) > 0

    isElement = staticmethod(isElement)

    def __signalRelationTypeChanged(self):
        """
        Emits the signal L{relationTypeChanged<AddEditRelationTypeDialog.relationTypeChanged>
        that indicates that relation type has changed.
        """

        self.emit(PYSIGNAL(relationTypeChanged), (self.__title, self.__iconName, self.__parentDataTypeList, self.__childDataTypeList, ))

    def _setAvailableDataTypeList(self, dataTypeList):
        self.__availableDataTypeList = dataTypeList

    def _getAvailableDataTypeList(self):
        return self.__availableDataTypeList

    def _setParentDataTypeList(self, dataTypeList):
        self.__parentDataTypeList = dataTypeList

    def _getParentDataTypeList(self):
        return self.__parentDataTypeList

    def _setChildDataTypeList(self, dataTypeList):
        self.__childDataTypeList = dataTypeList

    def _getChildDataTypeList(self):
        return self.__childDataTypeList

    def _setIconName(self, iconName):
        self.__iconName = iconName
        self.__signalRelationTypeChanged()

    def _getIconName(self):
        return self.__iconName

    def _setTitle(self, title):
        self.__title = title
        self.__signalRelationTypeChanged()

    def _getTitle(self):
        return self.__title

    myTitle = property(_getTitle, _setTitle)
    myIconName = property(_getIconName, _setIconName)
    myParentDataTypeList = property(_getParentDataTypeList, _setParentDataTypeList)
    myChildDataTypeList = property(_getChildDataTypeList, _setChildDataTypeList)
    myAvailableDataTypeList = property(_getAvailableDataTypeList, _setAvailableDataTypeList)
