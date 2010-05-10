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
Implements the functionality of the default authentication option page. 
"""


from qt import SIGNAL

from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$LastChangedRevision: 3906 $"


class AuthenticationOptionController(AbstractOptionController):
    """ Handles the standard authentication options. """
    
    def __init__(self, wizardView, wizardController, pageType):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
        
        AbstractOptionController.__init__(self, wizardView, wizardController, pageType)
        self.wizardView.connect(self.wizardView.userLineEdit, SIGNAL("textChanged(const QString&)"), self._userTextChanged)
        self.wizardView.connect(self.wizardView.passwordLineEdit, SIGNAL("textChanged(const QString&)"), self._passwordTextChanged)  
    
    def showModelPart(self):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.showModelPart>}
        """
        
        self.wizardView.authenticationOptionWidgetStack.raiseWidget(1)
        self.wizardView.userLineEdit.setText(self.wizardController.datastore.username or "")
        self.wizardView.passwordLineEdit.setText(self.wizardController.datastore.password or "")

    def _userTextChanged(self, username):
        """ Set and validate the username. """
        
        self.setDatastoreProperty("username", unicode(username), self.wizardView.userLineEdit)
            
    def _passwordTextChanged(self, password):
        """ Set and validate the password. """

        self.setDatastoreProperty("password", unicode(password), self.wizardView.passwordLineEdit)
    