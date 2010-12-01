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
Implements the functionality of the default storage option page. 
"""


from qt import SIGNAL

from datafinder.core.configuration.datastores.constants import STORAGE_REALISATION_MODE_ENUM
from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$Revision-Id:$" 


class StorageOptionController(AbstractOptionController):
    """ Default handler for the storage options of the DataStores. """
    
    def __init__(self, wizardView, wizardController, pageType):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
        
        AbstractOptionController.__init__(self, wizardView, wizardController, pageType)
        
        self.wizardView.storageRealisationComboBox.insertItem(STORAGE_REALISATION_MODE_ENUM.FLAT, 0)
        self.wizardView.storageRealisationComboBox.insertItem(STORAGE_REALISATION_MODE_ENUM.HIERARCHICAL, 1)
        self.wizardView.storageRealisationComboBox.setCurrentText(STORAGE_REALISATION_MODE_ENUM.HIERARCHICAL)
        
        self.wizardView.connect(self.wizardView.dataLocationLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._dataLocationTextChangedSlot)
        self.wizardView.connect(self.wizardView.isMigratedToCheckBox, SIGNAL("stateChanged(int)"), 
                                self._migratedToSlot)
        self.wizardView.connect(self.wizardView.isMigratedToLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._isMigratedToTextChangedSlot)
        self.wizardView.connect(self.wizardView.removePathPrefixLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._removePathPrefixTextChangedSlot)
        self.wizardView.connect(self.wizardView.storageRealisationComboBox, SIGNAL("activated(const QString&)"),
                                self._storageRealisationChangedSlot)
        
    def showModelPart(self):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.showModelPart>}
        """
        
        self.wizardView.storageOptionWidgetStack.raiseWidget(0)
        self.wizardView.dataLocationLineEdit.setText(self.wizardController.datastore.dataLocation or "")
        migratedTo = self.wizardController.datastore.isMigratedTo
        if not migratedTo is None and len(migratedTo) > 0:
            self.wizardView.isMigratedToLineEdit.setEnabled(True)
            self.wizardView.isMigratedToLineEdit.setText(migratedTo)
            self.wizardView.isMigratedToCheckBox.setChecked(True)
        else:
            self.wizardView.isMigratedToLineEdit.setEnabled(False)
            self.wizardView.isMigratedToLineEdit.setText("")
            self.wizardView.isMigratedToCheckBox.setChecked(False)
        storageRealisation = self.wizardController.datastore.storageRealisation
        self.wizardView.storageRealisationComboBox.setCurrentText(storageRealisation)
        self.wizardView.removePathPrefixLineEdit.setEnabled(storageRealisation != STORAGE_REALISATION_MODE_ENUM.FLAT)
        self.wizardView.removePathPrefixLineEdit.setText(self.wizardController.datastore.removePathPrefix or "")
            
    def _dataLocationTextChangedSlot(self, dataLocation):
        """ Set and validate the data location. """
        
        self.setDatastoreProperty("dataLocation", unicode(dataLocation), self.wizardView.dataLocationLineEdit)
        
    def _isMigratedToTextChangedSlot(self, migratedTo):
        """ Set and validate migrated to property. """
        
        self.setDatastoreProperty("isMigratedTo", unicode(migratedTo), self.wizardView.isMigratedToLineEdit)
        
    def _migratedToSlot(self, state):
        """ Handles changes of the "isMigratedToCheckBox". """

        if state:
            self.wizardView.isMigratedToLineEdit.setEnabled(True)
        else:
            self.wizardView.isMigratedToLineEdit.setText("")
            self.wizardView.isMigratedToLineEdit.setEnabled(False)
            
    def _removePathPrefixTextChangedSlot(self, removePathPrefix):
        """ Set and validate removePathPrefix property. """
        
        self.setDatastoreProperty("removePathPrefix", unicode(removePathPrefix), self.wizardView.removePathPrefixLineEdit)

    def _storageRealisationChangedSlot(self, storageRealisation):
        """ Sets the storage realization mode. """
        
        storageRealisation = str(storageRealisation)
        self.setDatastoreProperty("storageRealisation", storageRealisation, self.wizardView.storageRealisationComboBox)
        self.wizardView.removePathPrefixLineEdit.setEnabled(storageRealisation != STORAGE_REALISATION_MODE_ENUM.FLAT)
