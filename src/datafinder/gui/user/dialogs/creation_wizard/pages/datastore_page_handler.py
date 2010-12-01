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
Implements the specific data store wizard page.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.user.common.util import determineDisplayRepresentation
from datafinder.gui.user.dialogs.creation_wizard.constants import ALL_DATASTORE_MODE, ARCHIVE_DATASTORE_MODE, \
                                                                  OFFLINE_DATASTORE_MODE, ONLINE_DATASTORE_MODE
from datafinder.gui.user.dialogs.creation_wizard.pages.base_page import BaseWizardPage


__version__ = "$Revision-Id:$" 


class DataStoreWizardPage(BaseWizardPage):
    """ Implements the specific data store wizard page. """

    _DATASTORE_PROPERTY_DISPLAYNAME_MAP = {"storeType": "Type",
                                           "dataLocationUri": "Data Location URI",
                                           "description": "Description",
                                           "retentionPeriod": "Retention Period (days)",
                                           "readOnly": "Read-Only"}

    def __init__(self):
        """ Constructor. """
        
        BaseWizardPage.__init__(self)
        
        self.iconProvider = None
        self.dataStoreHandler = None
        self.preferences = None
        self.dataStoreMode = ALL_DATASTORE_MODE
        
        self._isInitialized = False
        self._dataStores = dict()
        
    def configure(self):
        """ Prepares the source index wizard page. """

        if not self._isInitialized:
            dataStores = list()
            for dataStore in self._determineDatastores():
                if dataStore.isDefault:
                    dataStores.insert(0, dataStore)
                else:
                    dataStores.append(dataStore)
            if len(dataStores) > 0:
                for dataStore in dataStores:
                    self._dataStores[dataStore.name] = dataStore
                    icon = self.iconProvider.iconForDataStore(dataStore)
                    if not icon is None:
                        self.dataStoreComboBox.addItem(icon, dataStore.name)
                    else:
                        self.dataStoreComboBox.addItem(dataStore.name)
                self.connect(self.dataStoreComboBox, QtCore.SIGNAL("activated(const QString)"), self._selectedDataStoreChanged)
                self._setInitialDataStore()
            self._isInitialized = True
        
    def _setInitialDataStore(self):
        """ Sets the initial data store. """
        
        defaultDataStoreName = self._determineLocalDefaultDataStoreName()
        currentIndex = self.dataStoreComboBox.findText(defaultDataStoreName)
        if currentIndex == -1:
            currentIndex = 0
        self.dataStoreComboBox.setCurrentIndex(currentIndex)
        self._selectedDataStoreChanged(unicode(self.dataStoreComboBox.currentText()))
        
    def _determineDatastores(self):
        """ Determines the data stores in accordance to the selected mode. """
        
        if self.dataStoreMode == ARCHIVE_DATASTORE_MODE:
            dataStores = self.dataStoreHandler.archiveDatastores
        elif self.dataStoreMode == ONLINE_DATASTORE_MODE:
            dataStores = self.dataStoreHandler.onlineDatastores
        elif self.dataStoreMode == OFFLINE_DATASTORE_MODE:
            dataStores = self.dataStoreHandler.offlineDatastores
        else:
            dataStores = self.dataStoreHandler.datastores
        return dataStores
    
    def _determineLocalDefaultDataStoreName(self):
        """ Finds out the suitable default data store stored in the preferences. """
    
        defaultDataStoreName = ""
        if self.dataStoreMode == ARCHIVE_DATASTORE_MODE:
            defaultDataStoreName = self.preferences.defaultArchiveStore or ""
        elif self.dataStoreMode == ONLINE_DATASTORE_MODE:
            defaultDataStoreName = self.preferences.defaultDataStore or ""
        elif self.dataStoreMode == OFFLINE_DATASTORE_MODE:
            defaultDataStoreName = self.preferences.defaultOfflineStore or ""
        return defaultDataStoreName
    
    def _selectedDataStoreChanged(self, dataStoreName):
        """ Handles changed selection of the data store. """

        dataStoreName = unicode(dataStoreName)
        if not dataStoreName in self._dataStores:
            dataStoreName = self._dataStores.keys()[0]
        dataStore = self._dataStores[unicode(dataStoreName)]
        
        self.dataStoreTableWidget.clear()
        row = 0
        self.dataStoreTableWidget.setRowCount(len(self._DATASTORE_PROPERTY_DISPLAYNAME_MAP))
        for dataStorePropertyName, displayName in self._DATASTORE_PROPERTY_DISPLAYNAME_MAP.iteritems():
            try:
                value = getattr(dataStore, dataStorePropertyName)
                value = determineDisplayRepresentation(value)
            except AttributeError:
                continue
            else:
                propertyNameItem = QtGui.QTableWidgetItem(displayName)
                valueItem = QtGui.QTableWidgetItem(unicode(value))
                self.dataStoreTableWidget.setItem(row, 0, propertyNameItem)
                self.dataStoreTableWidget.setItem(row, 1, valueItem)
                row += 1
        self.dataStoreTableWidget.setRowCount(row)
        self.dataStoreTableWidget.model().sort(0)

    @property
    def selectedDataStoreConfiguration(self):
        """ Returns the selected data store configuration. """
        
        return self._dataStores[unicode(self.dataStoreComboBox.currentText())]
