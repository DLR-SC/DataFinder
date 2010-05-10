#
# Created: 22.01.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: property_page.py 4450 2010-02-09 16:30:51Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the specific property wizard page.
"""


from PyQt4 import QtCore

from datafinder.core.configuration.properties.constants import DATATYPE_ID, DATASTORE_NAME_ID
from datafinder.gui.user.dialogs.creation_wizard.constants import INCOMPLETE_PROPERTY_DEFINITION
from datafinder.gui.user.dialogs.creation_wizard.pages.base_page import BaseWizardPage
from datafinder.gui.user.dialogs.creation_wizard.pages.utils import determineTargetDataTypes
from datafinder.gui.user.models.properties import PropertiesModel


__version__ = "$LastChangedRevision: 4450 $"


class PropertyWizardPage(BaseWizardPage):
    """ Implements the specific property wizard page. """

    def __init__(self):
        """ Constructor. """
        
        BaseWizardPage.__init__(self)
        self.index = None
        self.indexChanged = True
        self.baseRepositoryModel = None
        self.isDataTypeSelectionEnabled = True
        self.initialProperties = None
        
        self._dataTypes = dict()
        
    def configure(self):
        """ Prepares the source index wizard page. """

        if self.propertyWidget.model is None:
            self.propertyWidget.model = PropertiesModel(self.baseRepositoryModel, False)
            if self.isDataTypeSelectionEnabled:
                self.connect(self.propertyWidget.model, 
                             QtCore.SIGNAL(PropertiesModel.IS_CONSISTENT_SIGNAL),
                             self._handlePropertyConsistencySlot)
                self.connect(self.dataTypeComboBox, QtCore.SIGNAL("activated(const QString)"), self._selectedDataTypeChanged)
        
        if not self.wizard().dataStoreName is None:
            dataStoreProperty = self.baseRepositoryModel.repository.createProperty(DATASTORE_NAME_ID,
                                                                                   self.wizard().dataStoreName)
            if self.initialProperties is None:
                self.initialProperties = list()
            self.initialProperties.append(dataStoreProperty)
            self._loadProperties(self.initialProperties)
        
        if self.isDataTypeSelectionEnabled:
            self.dataTypeLabel.show()
            self.dataTypeComboBox.show()
            self._handleDataTypeProperties()
        else:
            self.dataTypeLabel.hide()
            self.dataTypeComboBox.hide()
        
    def _handleDataTypeProperties(self):
        """ Initializes data type specific property initializations. """
        
        if self.indexChanged:
            currentDataTypeName = unicode(self.dataTypeComboBox.currentText())
            self._dataTypes = dict()
            self.dataTypeComboBox.clear()
            targetDataTypes = determineTargetDataTypes(self.baseRepositoryModel, self.index)
            
            if len(targetDataTypes) > 0:
                for targetDataType in targetDataTypes:
                    self._dataTypes[targetDataType.name] = targetDataType
                    icon = self.baseRepositoryModel.iconProvider.iconForDataType(targetDataType)
                    if not icon is None:
                        self.dataTypeComboBox.addItem(icon, targetDataType.name)
                    else:
                        self.dataTypeComboBox.addItem(targetDataType.name)
                if not currentDataTypeName in self._dataTypes:
                    self._selectedDataTypeChanged(self._dataTypes.keys()[0])
        self._handlePropertyConsistencySlot(self.propertyWidget.model.isConsistent)
            
    def _selectedDataTypeChanged(self, dataTypeName):
        """ Handles changed selection of the data type. """
        
        dataType = self._dataTypes[unicode(dataTypeName)]
        dataTypeProperty = self.baseRepositoryModel.repository.createProperty(DATATYPE_ID,
                                                                              unicode(self.dataTypeComboBox.currentText()))
        properties = [dataTypeProperty]
        for propertyDefinition in dataType.propertyDefinitions:
            properties.append(propertyDefinition)
        self._loadProperties(properties)
            
    def _loadProperties(self, properties):
        """ Sets the given properties and resets the property model. """
        
        self.propertyWidget.model.load(properties)
        self.propertyWidget.model.reset()
        
    def _handlePropertyConsistencySlot(self, isConsistent):
        """ Slot handling the consistency of the property model. """
        
        if isConsistent:
            self.errorHandler.removeError(INCOMPLETE_PROPERTY_DEFINITION)
        else:
            errorMessage = "Please complete the missing property values."
            self.errorHandler.appendError(INCOMPLETE_PROPERTY_DEFINITION, errorMessage)
