# pylint: disable-msg=W0511
#
# Created: 23.03.2010 ney_mi <Miriam.Ney@dlr.de>
# Changed: $Id: authentication_option_controller.py 4561 2010-03-23 17:02:05Z ney_mi $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the functionality of the s3 authentication option page. 
"""


from qt import SIGNAL
from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$LastChangedRevision: 4561 $"


class AuthenticationOptionController(AbstractOptionController):
    """ Handles the authentication options of the ExternalWebDAV DataStore. """
    
    #TODO: Setting of Credentilals and Credential Options for the User
    
    def __init__(self, wizardView, wizardController, pageType):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
        
        #TODO: Adjust to S3
        AbstractOptionController.__init__(self, wizardView, wizardController, pageType)
        self.wizardView.externalWebDavPublicKeyLabel.hide()
        self.wizardView.externalWebDavPrivateKeyLabel.hide()
        self.wizardView.externalWebdavUploadPrivateKeyFilePushButton.hide()
        self.wizardView.externalWebdavUploadPublicKeyFilePushButton.hide()
        self.wizardView.connect(self.wizardView.externalWebdavUserLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._externalWebdavUserTextChanged)
        self.wizardView.connect(self.wizardView.externalWebdavPasswordLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._externalWebdavPasswordTextChanged)  