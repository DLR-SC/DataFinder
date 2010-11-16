#
# auth_connect_dialog.py
#
# Created: 16.11.2010 ney_mi <miriam.ney@dlr.de>
# Changed:
#
# Copyright (C) 2003-2007 DLR/SISTEC, Germany
#
# All rights reserved
#
# http://www.dlr.de/datafinder
#


"""
Connect dialog for entering the url, username, password of the WebDAV Server.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.gen.user.authentification_connect_dialog_ui import Ui_connectDialog

from datafinder.gui.user.dialogs.preferences_dialog import PreferencesDialogView
#from datafinder.gui.gen.user.connect_dialog_ui import Ui_connectDialog


__version__ = "$LastChangedRevision: 3989 $"


class AuthConnectDialogView(QtGui.QDialog, Ui_connectDialog):
    """
    The connection dialog is displayed when the datafinder has to establish a connection to
    a webdav server or any other server needing authentification information.
    This dialog contains field for entering a url and authentification credentials.
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
