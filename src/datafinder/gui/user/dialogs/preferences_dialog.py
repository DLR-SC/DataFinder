#
# preferences_dialog.py
#
# Created: 28.01.2008 wend_he <heinrich.wendel@dlr.de>
# Changed:
#
# Copyright (C) 2003-2007 DLR/SISTEC, Germany
#
# All rights reserved
#
# http://www.dlr.de/datafinder
#


"""
Dialog to configure connection preferences, currently only LDAP.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.gen.user.preferences_dialog_ui import Ui_preferencesDialog


__version__ = "$LastChangedRevision: 3989 $"


class PreferencesDialogView(QtGui.QDialog, Ui_preferencesDialog):
    """
    Dialog to configure connection preferences, currently only LDAP.
    """

    def __init__(self, parent=None):
        """
        Constructor.

        @param parent: Parent window of this L{QtGui.QDialog}
        @type parent: C{QtGui.QWidget}
        """

        QtGui.QDialog.__init__(self, parent)
        Ui_preferencesDialog.__init__(self)

        self.setupUi(self)

        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), self.reject)
        self.connect(self.okButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.useLdapCheckBox, QtCore.SIGNAL("stateChanged(int)"), self.useLdapStateChanged)

    def useLdapStateChanged(self, state):
        """
        Enables and disables the line edits to edit the ldap properties.
        
        @param state: The new state
        @type state C{Qt::CheckState}
        """
        if state == 2:
            self.serverUriLineEdit.setEnabled(True)
            self.baseDnLineEdit.setEnabled(True)
        else:
            self.serverUriLineEdit.setEnabled(False)
            self.baseDnLineEdit.setEnabled(False)
            
    def _getUseLdap(self):
        """
        Returns if ldap should be used.

        @return: If ldap should be used.
        @rtype: C{boolean}
        """

        if self.useLdapCheckBox.checkState() == 2:
            return True
        else:
            return False

    def _setUseLdap(self, use):
        """
        If ldap should be used.

        @param urls: If ldap should be used.
        @type urls: C{boolean}
        """
        if use:
            self.useLdapCheckBox.setCheckState(2)
        else:
            self.useLdapCheckBox.setCheckState(0)
            
    useLdap = property(_getUseLdap, _setUseLdap)
    
    def _getLdapServerUri(self):
        """
        Returns the ldap server uri.

        @return: The ldap server uri.
        @rtype: C{String}
        """
        return unicode(self.serverUriLineEdit.text())

    def _setLdapServerUri(self, uri):
        """
        Sets the ldap server uri.

        @param uri: The ldap server uri.
        @type uri: C{String}
        """
        self.serverUriLineEdit.setText(uri or "")
                
    ldapServerUri = property(_getLdapServerUri, _setLdapServerUri)
    
    def _getLdapBaseDn(self):
        """
        Returns the ldap basedn.

        @return: The ldap basedn.
        @rtype: C{String}
        """
        return unicode(self.baseDnLineEdit.text())

    def _setLdapBaseDn(self, basedn):
        """
        Sets the ldap basedn.

        @param basedn: The ldap basedn.
        @type basedn: C{String}
        """
        self.baseDnLineEdit.setText(basedn or "")
        
    ldapBaseDn = property(_getLdapBaseDn, _setLdapBaseDn)
    