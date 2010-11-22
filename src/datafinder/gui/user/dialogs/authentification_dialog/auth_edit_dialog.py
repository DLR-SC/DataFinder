#
# auth_connect_dialog.py
#
# Created: 16.11.2010 ney_mi <miriam.ney@dlr.de>
# Changed:
#
# Copyright (C) 2003-2010 DLR/SISTEC, Germany
#
# All rights reserved
#
# http://www.launchpad.net/datafinder
#


"""
Edit dialog to change authentification information such as url, username, password, ldap support
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.gen.user.authentification_edit_wizard_ui import Ui_editAuth

from datafinder.gui.user.dialogs.preferences_dialog import PreferencesDialogView


__version__ = "$Revision-Id:  $"


class AuthEditDialogView(QtGui.QDialog, Ui_editAuth, currentUri):
    """
    This dialog provides an interface to change credentials that belong to a specified connection
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
        Ui_editAuth.__init__(self)

        self.setupUi(self)
        
        self._preferences = preferences
        self._urlChangedSlot(currentUri)
                     
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

        return unicode(self.serverLineEdit.lineEdit().text())

    def _setUrl(self, urls):
        """
        Appends urls to the L{QtGui.QComboBox} widget.

        @param urls: A list of urls that has to be added.
        @type urls: C{list}
        """

        self.serverLineEdit.addItems(urls)

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

    def _getAuthentification(self):
        """
        Returns the authentification information from the password/certificate location field.

        @return: Returns the authentification information in the password field.
        @rtype: C{string}
        """

        return unicode(self.passwordLineEdit.text())

    def _setAuthentification(self, password):
        """
        Sets the password/credentials link in the credentials field.

        @param authentification: The credential information that has to be in the password/certificate location field.
        @type authentification: C{string}
        """

        self.authLineEdit.setText(authentification or "")

    def _getAuthMechanism(self):
        """
        Returns the authentification mechanism from the authentification mechanism field.

        @return: Returns the authentificationMechanism in the authentification mechanism field.
        @rtype: C{string}
        """
        return unicode(self.authMechanismCombo.text())
    
    def _setAuthMechansim (self, authMechanism):
        """
        Sets the authentification mechanism from the authentification mechanism field.

        @param: Integer to  the password field.
        @rtype: C{string}
        """
        self.authMechanismCombo.setCurrentIndex(authMechanism)
        
    def _getComment(self):
        """
        Returns the comment from the comment field.

        @return: Returns the comment in the comment field.
        @rtype: C{string}
        """
        return unicode(self.commentPlainText.text())

    def _setComment(self, comment):
        """
        Sets the comment from the comment field.

        @param: Sets the comment in the comment field.
        @rtype: C{string}
        """
        self.commentPlainText.setPlainText(comment)    
    
   
    uri = property(_getUrl, _setUrl)

    username = property(_getUsername, _setUsername)

    authentification = property(_getAuthentification, _setAuthentification)
    
    authMechanism = property (_getAuthMechanism, _setAuthMechanism)
    
    comment = property (_getComment, _setComment )
    
    

    
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
