# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
Implements the functionality of the base option page. 
"""


from qt import SIGNAL

from datafinder.core.configuration import datastores
from datafinder.gui.admin.datastore_configuration_wizard import constants
from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController
from datafinder.gui.admin.icon_selection_dialog import SelectUserIconDialog


__version__ = "$Revision-Id:$" 


class BaseOptionController(AbstractOptionController):
    """ Handler for the common DataStore options. """
    
    def __init__(self, wizardView, wizardController, pageType, dataStoreHandler, iconHandler):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
        
        AbstractOptionController.__init__(self, wizardView, wizardController, pageType)
        self._dataStoreHandler = dataStoreHandler
        self._iconHandler = iconHandler
        
        # init datastore ComboBox
        self.wizardView.datastoreTypeComboBox.clear()
        self.wizardView.datastoreTypeComboBox.insertItem(datastores.DEFAULT_STORE, 0)
        self.wizardView.datastoreTypeComboBox.insertItem(datastores.WEBDAV_STORE, 1)
        self.wizardView.datastoreTypeComboBox.insertItem(datastores.FTP_STORE, 2)
        self.wizardView.datastoreTypeComboBox.insertItem(datastores.FILE_STORE, 3)
        self.wizardView.datastoreTypeComboBox.insertItem(datastores.GRIDFTP_STORE, 4)
        self.wizardView.datastoreTypeComboBox.insertItem(datastores.OFFLINE_STORE, 5)
        self.wizardView.datastoreTypeComboBox.insertItem(datastores.TSM_CONNECTOR_STORE, 6)
        # make owner button invisible
        self.wizardView.datastoreOwnerPushButton.hide()
        # set labels for error displaying
        self.errorMessageLabel = self.wizardView.errorMessageLabel0
        self.errorMessagePixmapLabel = self.wizardView.errorMessagePixmapLabel0
        # select initial DataStore icon and type
        self.wizardView.setDatastoreIcon(self.wizardController.datastore.iconName)
        self.wizardView.datastoreTypeComboBox.setCurrentText(self.wizardController.datastore.storeType)
        # connect form specific slots
        self.wizardView.connect(self.wizardView.selectIconPushButton, SIGNAL("clicked()"), self._iconChangedSlot)
        self.wizardView.connect(self.wizardView.datastoreTypeComboBox, SIGNAL("activated(const QString&)"), 
                                self._datastoreTypeChangedSlot)
        self.wizardView.connect(self.wizardView.datastoreNameLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._datastoreNameTextChangedSlot)
        self.wizardView.connect(self.wizardView.datastoreOwnerLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._storeOwnerTextChangedSlot)
        self.wizardView.connect(self.wizardView.datafinderUrlLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._datafinderUrlTextChangedSlot)
        self.wizardView.connect(self.wizardView.defaultDatastoreCheckBox, SIGNAL("stateChanged(int)"), 
                                self._storeDefaultStateChangedSlot)
              
    def showModelPart(self):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.showModelPart>}
        """
        
        self.wizardView.datastoreNameLineEdit.setText(self.wizardController.datastore.name or "")
        self.wizardView.datastoreOwnerLineEdit.setText(self.wizardController.datastore.owner or "")
        self.wizardView.datafinderUrlLineEdit.setText(self.wizardController.datastore.url or "")
        self.wizardView.defaultDatastoreCheckBox.setChecked(self.wizardController.datastore.isDefault)
            
    def _datastoreNameTextChangedSlot(self, newName):
        """ Set and check DataStore name. """
        
        self.setDatastoreProperty("name", unicode(newName), self.wizardView.datastoreNameLineEdit)
        self.wizardView.setCaption(constants.wizardCaptionTemplate % (self.wizardController.datastore.storeType, 
                                   self.wizardController.datastore.name))
        
    def _storeOwnerTextChangedSlot(self, newOwner):
        """ Set and check DataStore owner. """
        
        self.setDatastoreProperty("owner", unicode(newOwner), self.wizardView.datastoreOwnerLineEdit)
    
    def _datafinderUrlTextChangedSlot(self, newDatafinderUrl):
        """ Set and check DataFinder Url. """
        
        self.setDatastoreProperty("url", unicode(newDatafinderUrl), self.wizardView.datafinderUrlLineEdit)
        
    def _storeDefaultStateChangedSlot(self, state):
        """ Set and check the option if this is a default DataStore. """ 
        
        if state:
            self.setDatastoreProperty("isDefault", True, self.wizardView.defaultDatastoreCheckBox)
        else:
            self.setDatastoreProperty("isDefault", False, self.wizardView.defaultDatastoreCheckBox)
    
    def _datastoreTypeChangedSlot(self, newStoreTypeQString):
        """ Handles the change of the DataStore type. """
        
        newStoreType = unicode(newStoreTypeQString)
        if self.wizardController.datastore.storeType != newStoreType: 
            newDatastore = self._dataStoreHandler.createDataStore(storeType=newStoreType)
            oldDatastore = self.wizardController.datastore
            # save values of current datastore
            newDatastore.name = oldDatastore.name
            newDatastore.owner = oldDatastore.owner
            newDatastore.url = oldDatastore.url
            newDatastore.isDefault = oldDatastore.isDefault
            newDatastore.iconName = oldDatastore.iconName
            self.wizardController.datastore = newDatastore
            self.wizardView.setCaption(constants.wizardCaptionTemplate % (self.wizardController.datastore.storeType, 
                                       self.wizardController.datastore.name))
            self.wizardController.setPageSequence()
            self.checkErrorMessageDisplaying()
   
    def _iconChangedSlot(self):
        """ Handles the changes of the DataStore icon. """
        
        selectIconDialog = SelectUserIconDialog()
        iconNames = selectIconDialog.getIconName(self._iconHandler.allIcons, self.wizardController.datastore.iconName)
        if len(iconNames) > 0 and not iconNames[0] == self.wizardController.datastore.iconName:
            self.wizardController.datastore.iconName = unicode(iconNames[0])
            self.wizardView.setDatastoreIcon(iconNames[0])
