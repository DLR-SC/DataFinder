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
Provides tests for the credential update dialog.
"""


import sys
import unittest

from PyQt4 import QtGui

from datafinder.gui.user.dialogs.datastore_dialog import DataStoreCredentialUpdateDialog
from datafinder_test import mocks


__version__ = "$Revision-Id:$" 


def _callback(credentials):
    if credentials["password"] == "wrong_secret":
        return False
    else:
        return True

class DataStoreCredentialUpdateTest(unittest.TestCase):
    """ Implements test cases of the update credential dialog. """
    # problem of unittest: pylint: disable=R0904
    
    @classmethod
    def setUpClass(cls):
        cls._application = QtGui.QApplication(sys.argv) # Initializes the Qt framework once

    @classmethod
    def tearDown(cls):
        cls._application.exit()
        
    def setUp(self): 
        # Fine for testing: pylint: disable=W0212
        
        self._dialog = DataStoreCredentialUpdateDialog(
            mocks.SimpleMock(name="DataStore"), _callback)
        self._view = self._dialog._view
        
    def testInitialState(self):
        self.assertNotEqual(self._view.errorLabel.text(), "")

    def testUpdateSuccess(self):
        self._view.username_input.setText("user")
        self._view.password_input.setText("secret")
        
        self._view.retryButton.click()
        self._waitUntilFinished()
        
        self.assertEqual(self._view.errorLabel.text(), 
            "The data store 'DataStore' could be successfully accessed!")
    
    def _waitUntilFinished(self):
        # Fine for testing: pylint: disable=W0212
        
        while not self._dialog._workerThread.isFinished():
            pass
        # Need to to this manually, thread callback will not be called in this test setup
        self._dialog._evaluateCredentialUpdate()
        
    def testUpdateFailure(self):
        self._view.password_input.setText("wrong_secret")
        self._view.retryButton.click()
        self._waitUntilFinished()
        
        self.assertNotEqual(self._view.errorLabel.text(), "")

    def testUpdateRecovery(self):
        self.testUpdateSuccess()
        self.testUpdateFailure()
        self.testUpdateSuccess()
        self.testUpdateSuccess()
        self.testUpdateFailure()
        self.testUpdateFailure()
        self.testUpdateSuccess()


if __name__ == "__main__": # allows manual testing of the dialog
    application = QtGui.QApplication(sys.argv)
    dialog = DataStoreCredentialUpdateDialog(mocks.SimpleMock(name="DataStore"), _callback)
    dialog.exec_()
