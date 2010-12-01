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
Implements the functionality of the TSM storage option page. 
"""


from qt import SIGNAL

from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$Revision-Id:$" 


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
