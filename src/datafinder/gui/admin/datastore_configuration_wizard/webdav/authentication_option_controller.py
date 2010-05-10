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
Implements the functionality of the WebDAV authentication option page. 
"""


from qt import SIGNAL
from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$LastChangedRevision: 3906 $"


class AuthenticationOptionController(AbstractOptionController):
    """ Handles the authentication options of the ExternalWebDAV DataStore. """
    
    def __init__(self, wizardView, wizardController, pageType):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
        
        AbstractOptionController.__init__(self, wizardView, wizardController, pageType)
        self.wizardView.externalWebDavPublicKeyLabel.hide()
        self.wizardView.externalWebDavPrivateKeyLabel.hide()
        self.wizardView.externalWebdavUploadPrivateKeyFilePushButton.hide()
        self.wizardView.externalWebdavUploadPublicKeyFilePushButton.hide()
        self.wizardView.connect(self.wizardView.externalWebdavUserLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._externalWebdavUserTextChanged)
        self.wizardView.connect(self.wizardView.externalWebdavPasswordLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._externalWebdavPasswordTextChanged)  
    
    def showModelPart(self):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.showModelPart>}
        """
        
        self.wizardView.authenticationOptionWidgetStack.raiseWidget(2)
        self.wizardView.externalWebdavUserLineEdit.setText(self.wizardController.datastore.username or "")
        self.wizardView.externalWebdavPasswordLineEdit.setText(self.wizardController.datastore.password or "")
            
    def _externalWebdavUserTextChanged(self, username):
        """ Set and validate the username. """
        
        self.setDatastoreProperty("username", unicode(username), self.wizardView.externalWebdavUserLineEdit)
            
    def _externalWebdavPasswordTextChanged(self, password):
        """ Set and validate the password. """

        self.setDatastoreProperty("password", unicode(password), self.wizardView.externalWebdavPasswordLineEdit)
