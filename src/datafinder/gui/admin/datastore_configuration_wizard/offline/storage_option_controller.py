#
# Created: 10.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: storage_option_controller.py 3603 2008-12-01 13:26:31Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the functionality of the offline data store storage option page. 
"""


from qt import SIGNAL

from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$LastChangedRevision: 3603 $"


class StorageOptionController(AbstractOptionController):
    """ Handles the storage options of the Offline DataStore. """
    
    def __init__(self, wizardView, wizardController, pageType):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
        
        AbstractOptionController.__init__(self, wizardView, wizardController, pageType)
        self.wizardView.connect(self.wizardView.offlineDatastoreDataLocationLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._dataLocationTextChangedSlot)
        
    def showModelPart(self):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.showModelPart>}
        """
        
        self.wizardView.storageOptionWidgetStack.raiseWidget(1)
        self.wizardView.offlineDatastoreDataLocationLineEdit.setText(self.wizardController.datastore.dataLocation)
            
    def _dataLocationTextChangedSlot(self, dataLocation):
        """ Set and validate the data location. """
        
        self.setDatastoreProperty("dataLocation", unicode(dataLocation), self.wizardView.dataLocationLineEdit)
