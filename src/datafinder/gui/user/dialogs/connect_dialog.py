#
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#met:
#
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
Connect dialog for entering the url, username, password of the WebDAV Server.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.user.dialogs.preferences_dialog import PreferencesDialogView
from datafinder.gui.gen.user.connect_dialog_ui import Ui_connectDialog


__version__ = "$Revision-Id:$" 


class ConnectDialogView(QtGui.QDialog, Ui_connectDialog):
    """
    The connection dialog is displayed when the datafinder has to establish a connection to
    a webdav server.
    This dialog contains field for entering a url, username and password.
    """

    def __init__(self, parent=None, preferences=None):
        """
        Constructor.

        @param parent: Parent window of this L{QtGui.QDialog}
        @type parent: C{QtGui.QWidget}
        @param preferences: The preferences object.
        @type preferences: L{PreferencesHandler<datafinder.core.configuration.preferences.PreferencesHandler>}
        """

        QtGui.QDialog.__init__(self, parent)
        Ui_connectDialog.__init__(self)

        self.setupUi(self)
        
        self._preferences = preferences
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), self.reject)
        self.connect(self.connectButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.urlComboBox, QtCore.SIGNAL("currentIndexChanged(const QString)"), self._urlChangedSlot)
        self.connect(self.preferencesButton, QtCore.SIGNAL("clicked()"), self._preferencesActionSlot)
        self.uri = preferences.connectionUris
                     
    def _urlChangedSlot(self, newUri):
        """ Implementing changing of connection URI. """
        
        uri = unicode(newUri)
        connection = self._preferences.getConnection(uri)
        if not connection is None:
            self.username = connection.username
            self.password = connection.password
            self.savePasswordFlag = not connection.password is None
    
    def _getUrl(self):
        """
        Returns the entered url.

        @return: The url that was entered in the combobox.
        @rtype: C{string}
        """

        return unicode(self.urlComboBox.lineEdit().text())

    def _setUrl(self, urls):
        """
        Appends urls to the L{QtGui.QComboBox} widget.

        @param urls: A list of urls that has to be added.
        @type urls: C{list}
        """

        self.urlComboBox.addItems(urls)

    def _getUsername(self):
        """
        Returns the username that was entered by the user.

        @return: The username that was entered.
        @rtype: C{string}
        """

        return unicode(self.usernameLineEdit.text())

    def _setUsername(self, username):
        """
        Set a string that in the username field.

        @param username: The username that has to be in the username field.
        @type username: C{string}
        """

        self.usernameLineEdit.setText(username or "")

    def _getPassword(self):
        """
        Returns the password from the password field.

        @return: Returns the password in the password field.
        @rtype: C{string}
        """

        return unicode(self.passwordLineEdit.text())

    def _setPassword(self, password):
        """
        Sets the password in the password field.

        @param password: The password that has to be in the password field.
        @type password: C{string}
        """

        self.passwordLineEdit.setText(password or "")

    def _getSavePassword(self):
        """
        Returns true when the save password L{QtGui.QCheckBox} is checked else false.

        @return: True when the L{QtGui.QCheckBox} is checked else False.
        @rtype: C{boolean}
        """

        return self.savePasswordCheckBox.isChecked()

    def _setSavePassword(self, checked):
        """
        Set the state of the save password L{QtGui.QCheckBox}.

        @param checked: True when the L{QtGui.QCheckBox} has to be checked else False.
        @type checked: C{boolean}
        """

        self.savePasswordCheckBox.setChecked(checked)

    def _setShowUrl(self, show):
        """
        Show or hide the server groupbox by the given show parameter.

        @param show: True when the server groupbox has to be shown else False.
        @type show: C{boolean}
        """

        self.serverGroupBox.setHidden(not show)

    uri = property(_getUrl, _setUrl)

    username = property(_getUsername, _setUsername)

    password = property(_getPassword, _setPassword)

    savePasswordFlag = property(_getSavePassword, _setSavePassword)

    showUrl = property(fset=_setShowUrl)
    
    def _preferencesActionSlot(self):
        """ Shows the preferences dialog for connection settings. """

        preferencesDialog = PreferencesDialogView(self)

        preferencesDialog.useLdap = self._preferences.useLdap
        preferencesDialog.ldapBaseDn = self._preferences.ldapBaseDn
        preferencesDialog.ldapServerUri = self._preferences.ldapServerUri

        if preferencesDialog.exec_() == QtGui.QDialog.Accepted:
            self._preferences.useLdap = preferencesDialog.useLdap
            self._preferences.ldapBaseDn = preferencesDialog.ldapBaseDn
            self._preferences.ldapServerUri = preferencesDialog.ldapServerUri
            self._preferences.store()
