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
Implements the functionality of the default storage option page. 
"""


from qt import SIGNAL

from datafinder.core.configuration.datastores.constants import STORAGE_REALISATION_MODE_ENUM
from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$LastChangedRevision: 4063 $"


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
