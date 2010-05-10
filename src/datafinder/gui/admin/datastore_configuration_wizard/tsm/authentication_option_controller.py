#
# Created: 10.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: authentication_option_controller.py 3906 2009-04-03 17:17:43Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the functionality of the TSM authentication option page. 
"""


from qt import SIGNAL

from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$LastChangedRevision: 3906 $"


class AuthenticationOptionController(AbstractOptionController):
    """ Handles the authentication options of the TSM Connector DataStore. """
    
    def __init__(self, wizardView, wizardController, pageType):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
        
        AbstractOptionController.__init__(self, wizardView, wizardController, pageType)
        self.wizardView.connect(self.wizardView.tsmHostUserLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._hostUserTextChanged)
        self.wizardView.connect(self.wizardView.tsmHostPasswordLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._hostPasswordTextChanged)  
    
    def showModelPart(self):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.showModelPart>}
        """
        
        self.wizardView.authenticationOptionWidgetStack.raiseWidget(3)
        self.wizardView.tsmHostUserLineEdit.setText(self.wizardController.datastore.username)
        self.wizardView.tsmHostPasswordLineEdit.setText(self.wizardController.datastore.password)

    def _hostUserTextChanged(self, username):
        """ Set and validate the username for the host authentication. """
        
        self.setDatastoreProperty("username", unicode(username), self.wizardView.tsmHostUserLineEdit)
            
    def _hostPasswordTextChanged(self, password):
        """ Set and validate the password for the host authentication. """
        
        self.setDatastoreProperty("password", unicode(password), self.wizardView.tsmHostPasswordLineEdit)
