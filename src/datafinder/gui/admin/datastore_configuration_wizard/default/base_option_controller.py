#
# Created: 10.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: base_option_controller.py 4100 2009-05-24 18:12:19Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the functionality of the base option page. 
"""


from qt import SIGNAL

from datafinder.core.configuration import datastores
from datafinder.gui.admin.datastore_configuration_wizard import constants
from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController
from datafinder.gui.admin.icon_selection_dialog import SelectUserIconDialog


__version__ = "$LastChangedRevision: 4100 $"


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
