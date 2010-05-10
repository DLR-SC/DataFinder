#
# Created: 10.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: security_option_controller.py 3906 2009-04-03 17:17:43Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the functionality of the GridFTP security option page. 
"""


from qt import SIGNAL

from datafinder.core.configuration.datastores import GRIDFTP_SECURITY_MODE_ENUM
from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$LastChangedRevision: 3906 $"


class SecurityOptionController(AbstractOptionController):
    """ Handles the security options of the GridFTP DataStore. """
    
    def __init__(self, wizardView, wizardController, pageType):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
        
        AbstractOptionController.__init__(self, wizardView, wizardController, pageType)
        # init security modes
        self.wizardView.gridFtpSecurityModeComboBox.insertItem(GRIDFTP_SECURITY_MODE_ENUM.STANDARD, 0)
        self.wizardView.gridFtpSecurityModeComboBox.insertItem(GRIDFTP_SECURITY_MODE_ENUM.SAFE, 1)
        self.wizardView.gridFtpSecurityModeComboBox.insertItem(GRIDFTP_SECURITY_MODE_ENUM.PRIVATE, 2)
        self.wizardView.connect(self.wizardView.gridFtpSecurityModeComboBox, SIGNAL("activated(const QString&)"), 
                                self._gridFtpSecurityModeChangedSlot)
    
    def showModelPart(self):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.showModelPart>}
        """
        
        self.wizardView.securityOptionsWidgetStack.raiseWidget(0)
        self.wizardView.gridFtpSecurityModeComboBox.setCurrentText(self.wizardController.datastore.securityMode)
        
    def _gridFtpSecurityModeChangedSlot(self, securityMode):
        """ Set and validate security mode of the GridFTP DataStore. """

        self.setDatastoreProperty("securityMode", str(securityMode), self.wizardView.gridFtpSecurityModeComboBox)
