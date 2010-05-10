# pylint: disable-msg=W0511

# Created: 23.03.2010 ney_mi <Miriam.Ney@dlr.de>
# Changed: $Id: storage_option_controller.py 4561 2010-03-23 17:02:05Z ney_mi $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the functionality of the s3 storage option page. 
"""


from qt import SIGNAL

from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$LastChangedRevision: 4561 $"


class StorageOptionController(AbstractOptionController):
    """ Handles the storage options of the s3 Connector DataStore. """
    
    #TODO: Definition of Bucketname and generation of Keynames
    #TODO: Definition of layout structure: flatstore plus hierarchical view for everyone else
    
    def __init__(self, wizardView, wizardController, pageType):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
        
        #TODO: Adjust to S3
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