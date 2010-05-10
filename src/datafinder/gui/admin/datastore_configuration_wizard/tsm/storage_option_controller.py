#
# Created: 10.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: storage_option_controller.py 4063 2009-05-15 15:41:51Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the functionality of the TSM storage option page. 
"""


from qt import SIGNAL

from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$LastChangedRevision: 4063 $"


class StorageOptionController(AbstractOptionController):
    """ Handles the storage options of the TSM Connector DataStore. """

    def __init__(self, wizardView, wizardController, pageType):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
       
        AbstractOptionController.__init__(self, wizardView, wizardController, pageType)
        self.wizardView.connect(self.wizardView.tsmClientHostNameLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._clientHostNameTextChangedSlot)
        self.wizardView.connect(self.wizardView.tsmServerNodeNameLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._serverNodeNameTextChangedSlot)
        self.wizardView.connect(self.wizardView.tsmArchiveRootDirectoryLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._archiveRootDirectoryTextChangedSlot)
        self.wizardView.connect(self.wizardView.archiveDescriptionLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._archiveDescriptionTextChangedSlot)
        self.wizardView.connect(self.wizardView.archiveRetentionPeriodSpinBox, SIGNAL("valueChanged(int)"), 
                                self._archiveRetentionPeriodValueChanged)
        self.wizardView.connect(self.wizardView.archiveReadOnlyCheckBox, SIGNAL("stateChanged(int)"), 
                                self._archiveReadOnlyChangedSlot)
        self.wizardView.connect(self.wizardView.tsmIsMigratedToCheckBox, SIGNAL("stateChanged(int)"), 
                                self._migratedToSlot)
        self.wizardView.connect(self.wizardView.tsmIsMigratedToLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._isMigratedToTextChangedSlot)
                                
    def showModelPart(self):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.showModelPart>}
        """
        
        self.wizardView.storageOptionWidgetStack.raiseWidget(2)
        self.wizardView.tsmClientHostNameLineEdit.setText(self.wizardController.datastore.clientHostName)
        self.wizardView.tsmServerNodeNameLineEdit.setText(self.wizardController.datastore.serverNodeName)
        self.wizardView.tsmArchiveRootDirectoryLineEdit.setText(self.wizardController.datastore.archiveRootDirectory)
        self.wizardView.archiveDescriptionLineEdit.setText(self.wizardController.datastore.description)
        self.wizardView.archiveRetentionPeriodSpinBox.setValue(self.wizardController.datastore.retentionPeriod)
        self.wizardView.archiveReadOnlyCheckBox.setChecked(self.wizardController.datastore.readOnly)
        
        migratedTo = self.wizardController.datastore.isMigratedTo
        if not migratedTo is None and len(migratedTo) > 0:
            self.wizardView.tsmIsMigratedToLineEdit.setEnabled(True)
            self.wizardView.tsmIsMigratedToLineEdit.setText(migratedTo)
            self.wizardView.tsmIsMigratedToCheckBox.setChecked(True)
        else:
            self.wizardView.tsmIsMigratedToLineEdit.setEnabled(False)
            self.wizardView.tsmIsMigratedToLineEdit.setText("")
            self.wizardView.tsmIsMigratedToCheckBox.setChecked(False)
        
    def _clientHostNameTextChangedSlot(self, clientHostName):
        """ Set and validate the TSM client host name. """
        
        self.setDatastoreProperty("clientHostName", unicode(clientHostName), self.wizardView.tsmClientHostNameLineEdit)
   
    def _serverNodeNameTextChangedSlot(self, serverNodeName):
        """ Set and validate the TSM server node name. """
        
        self.setDatastoreProperty("serverNodeName", unicode(serverNodeName), self.wizardView.tsmServerNodeNameLineEdit)
   
    def _archiveRootDirectoryTextChangedSlot(self, archiveRootDirectory):
        """ Set and validate the TSM archiving root directory. """
        
        self.setDatastoreProperty("archiveRootDirectory", unicode(archiveRootDirectory), self.wizardView.tsmArchiveRootDirectoryLineEdit)
        
    def _archiveDescriptionTextChangedSlot(self, description):
        """ Set and validate the archive description. """
        
        self.setDatastoreProperty("description", unicode(description), self.wizardView.archiveDescriptionLineEdit)
    
    def _archiveRetentionPeriodValueChanged(self, newValue):
        """ Set and validate the archive retention period. """
        
        self.setDatastoreProperty("retentionPeriod", newValue, self.wizardView.archiveRetentionPeriodSpinBox)
        
    def _archiveReadOnlyChangedSlot(self, newValue):
        """ Reacts to changes of the read only property. """
        
        self.setDatastoreProperty("readOnly", bool(newValue), self.wizardView.archiveReadOnlyCheckBox)

    def _isMigratedToTextChangedSlot(self, migratedTo):
        """ Set and validate migrated to property. """
        
        self.setDatastoreProperty("isMigratedTo", unicode(migratedTo), self.wizardView.tsmIsMigratedToLineEdit)
        
    def _migratedToSlot(self, state):
        """ Handles changes of the "isMigratedToCheckBox". """

        if state:
            self.wizardView.tsmIsMigratedToLineEdit.setEnabled(True)
        else:
            self.wizardView.tsmIsMigratedToLineEdit.setText("")
            self.wizardView.tsmIsMigratedToLineEdit.setEnabled(False)
