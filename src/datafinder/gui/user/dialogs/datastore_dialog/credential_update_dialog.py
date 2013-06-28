# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2013, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
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
Provides a dialog to handle credential/authentication information updates for data store.
Via callbacks the authentication information of the centrally managed file systems can be directly updated.
Currently, we just support simple username/password authentication.
"""


from PyQt4 import QtGui
from PyQt4.QtGui import QDialogButtonBox
from PyQt4 import QtCore

from datafinder.gui.gen.user import datastore_credential_update_dialog_ui
from datafinder.gui.user.common import util


__version__ = "$Revision-Id:$" 


class DataStoreCredentialUpdateView(datastore_credential_update_dialog_ui.Ui_CredentialUpdateDialog, QtGui.QDialog):
    """ View component of the dialog which provides a simplified interface to the GUI elements. """
      
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        datastore_credential_update_dialog_ui.Ui_CredentialUpdateDialog.__init__(self)
        self.setupUi(self)
        
    @property
    def retryButton(self):
        """ Provides access to the Retry button. """
        
        return self.buttons.button(QDialogButtonBox.Retry)

    def indicateMessage(self, message):
        """ Shows the error message. """
        
        self.errorLabel.show()
        self.errorLabel.setText(message)

        
class DataStoreCredentialUpdateController(QtCore.QObject):
    """ Handles the interaction with the user. """
    
    def __init__(self, datastore, credentialUpdateCallback, parent=None):
        """
        @param datastore: Data store configuration to show the user some details.
        @type datastore: L{DefaultDataStore<datafinder.core.configuration.datastores.datastore.DefaultDataStore>}
        @param credentialUpdateCallback: Callback function to set new credentials.
        @see: L{AuthenticationError<datafinder.core.error.AuthenticationError>} for details about the callback.
        @param parent: The parent widget of the dialog.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """

        QtCore.QObject.__init__(self)
        
        self._datastore = datastore
        self._credentialUpdateCallback = credentialUpdateCallback
        self._view = DataStoreCredentialUpdateView(parent)
        self._workerThread = None
        
        self._view.retryButton.clicked.connect(self._performCredentialUpdate)
        
        self._indicateErrorMessage()
        
    def _indicateErrorMessage(self):
        message = (
            "The data store '%s' can currently not be accessed.\n"
            "You can try to provide new authentication information\n"
            "and retry to establish the connection."
            % self._datastore.name)
        self._view.indicateMessage(message)
        
    def _indicateSuccessMessage(self):
        message = (
            "The data store '%s' could be successfully accessed!"
            % self._datastore.name)
        self._view.indicateMessage(message)
        
    def _performCredentialUpdate(self):
        username = unicode(self._view.username_input.text())
        password = unicode(self._view.password_input.text())
        credentials = {"username": username, "password": password}
        self._view.retryButton.setEnabled(False)
        self._workerThread = util.startNewQtThread(lambda: self._credentialUpdateCallback(credentials), self._evaluateCredentialUpdate)
        
    def _evaluateCredentialUpdate(self):
        if self._workerThread.result:
            self._indicateSuccessMessage()
        else:
            self._indicateErrorMessage()
        self._view.retryButton.setEnabled(True)
        
    def show(self):
        """ Delegates to view. """
        
        return self._view.show()
    
    def exec_(self):
        """ Delegates to view. """
        
        return self._view.exec_()
