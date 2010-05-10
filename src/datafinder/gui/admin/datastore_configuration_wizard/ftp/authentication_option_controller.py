#
# Created: 10.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: authentication_option_controller.py 3920 2009-04-08 11:42:11Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the functionality of the FTP authentication option page. 
"""


from qt import SIGNAL

from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$LastChangedRevision: 3920 $"


class AuthenticationOptionController(AbstractOptionController):
    """ Handles the authentication options of the FTP DataStore. """
    
    def __init__(self, wizardView, wizardController, pageType):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
        
        AbstractOptionController.__init__(self, wizardView, wizardController, pageType)
        self.wizardView.connect(self.wizardView.anonymousFtpCheckBox, SIGNAL("stateChanged(int)"), self._anonymousFtpSlot)
        self.wizardView.connect(self.wizardView.ftpUserLineEdit, SIGNAL("textChanged(const QString&)"), self._ftpUserTextChanged)
        self.wizardView.connect(self.wizardView.ftpPasswordLineEdit, SIGNAL("textChanged(const QString&)"), self._ftpPasswordTextChanged)  
    
    def showModelPart(self):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.showModelPart>}
        """
        
        self.wizardView.disconnect(self.wizardView.anonymousFtpCheckBox, SIGNAL("stateChanged(int)"), self._anonymousFtpSlot)
        self.wizardView.authenticationOptionWidgetStack.raiseWidget(0)
        self.wizardView.ftpUserLineEdit.setText(self.wizardController.datastore.username or "")
        self.wizardView.ftpPasswordLineEdit.setText(self.wizardController.datastore.password or "")
        isAnonymousAuthentication = self.wizardController.datastore.isAnonymousAuthenticationEnabled
        self.wizardView.anonymousFtpCheckBox.setChecked(isAnonymousAuthentication)
        self._setInputElementState(not isAnonymousAuthentication)
        self.wizardView.connect(self.wizardView.anonymousFtpCheckBox, SIGNAL("stateChanged(int)"), self._anonymousFtpSlot)
        
    def _setInputElementState(self, enableState):
        """ Set the enabled state of the LineEdit GUI elements. """
        
        self.wizardView.ftpUserLineEdit.setEnabled(enableState)
        self.wizardView.ftpPasswordLineEdit.setEnabled(enableState)
        
    def _anonymousFtpSlot(self, state):
        """ Handles anonymousFtpCheckBox changes. """
        
        self.wizardController.datastore.isAnonymousAuthenticationEnabled = bool(state)
        if state:
            self.wizardView.ftpUserLineEdit.setText("")
            self.wizardView.ftpPasswordLineEdit.setText("")
        self._setInputElementState(not state)
        
    def _ftpUserTextChanged(self, username):
        """ Set and validate the username. """
        
        self.setDatastoreProperty("username", unicode(username), self.wizardView.ftpUserLineEdit)
            
    def _ftpPasswordTextChanged(self, password):
        """ Set and validate the password. """

        self.setDatastoreProperty("password", unicode(password), self.wizardView.ftpPasswordLineEdit)
