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
Implements the functionality of the WebDAV authentication option page. 
"""


from qt import SIGNAL
from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$Revision-Id:$" 


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
