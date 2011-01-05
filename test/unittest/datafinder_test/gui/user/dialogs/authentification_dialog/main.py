# $Filename$$
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
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
Allows simplified start of the authentification dialog.
"""


import sys

from PyQt4.QtGui import QApplication
from datafinder.gui.user.dialogs.authentification_dialog.auth_connect_dialog import AuthConnectDialogView
from datafinder.gui.user.dialogs.connect_dialog import ConnectDialogView
from datafinder.core.configuration.gen import preferences

__version__ = "$Revision-Id$" 


if __name__ == "__main__":
    connection = preferences.connection("http://test/test", "usertest", "passwordtest", None, None, None)
    connection.name = "usertest"
    connection.password = "passwordtest"
    connection.uri = "http://test/test"
    class TestPreferences(object):
        connectionUris = list()
        connectionUris.append(connection.uri)
          
        # for preferences dialog
        useLdap = "true"
        ldapBaseDn ="me"
        ldapServerUri = "test/uri"
        
        @staticmethod
        def getConnection(uri):
            return connection
  
        
    application = QApplication(sys.argv)
    dialog = AuthConnectDialogView(TestPreferences)
    #dialog = ConnectDialogView(None, TestPreferences)
    dialog.show()
    sys.exit(application.exec_())
