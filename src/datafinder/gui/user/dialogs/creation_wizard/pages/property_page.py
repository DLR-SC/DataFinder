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
Implements the specific property wizard page.
"""


from PyQt4 import QtCore

from datafinder.core.configuration.properties.constants import DATATYPE_ID, DATASTORE_NAME_ID
from datafinder.gui.user.dialogs.creation_wizard.constants import INCOMPLETE_PROPERTY_DEFINITION
from datafinder.gui.user.dialogs.creation_wizard.pages.base_page import BaseWizardPage
from datafinder.gui.user.dialogs.creation_wizard.pages.utils import determineTargetDataTypes
from datafinder.gui.user.models.properties import PropertiesModel


__version__ = "$Revision-Id:$" 


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
        for propDef in dataType.propertyDefinitions:
            prop = self.baseRepositoryModel.repository.createPropertyFromDefinition(propDef, propDef.defaultValue)
            properties.append(prop)
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
