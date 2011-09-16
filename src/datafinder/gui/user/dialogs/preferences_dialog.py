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
Dialog to configure connection preferences, currently only LDAP.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.gen.user.preferences_dialog_ui import Ui_preferencesDialog


__version__ = "$Revision-Id:$" 


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
        self.connect(self.useLuceneCheckBox, QtCore.SIGNAL("stateChanged(int)"), self.useLuceneStateChanged)

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
    
    def useLuceneStateChanged(self, state):
        """
        Enables and disables the line edits to edit the lucene properties.
        
        @param state: The new state
        @type state C{Qt::CheckState}
        """
        if state == 2:
            self.indexUriLineEdit.setEnabled(True)
        else:
            self.indexUriLineEdit.setEnabled(False)
            
    def _getUseLucene(self):
        """
        Returns if lucene should be used.

        @return: If lucene should be used.
        @rtype: C{boolean}
        """

        if self.useLuceneCheckBox.checkState() == 2:
            return True
        else:
            return False

    def _setUseLucene(self, use):
        """
        If lucene should be used.

        @param urls: If lucene should be used.
        @type urls: C{boolean}
        """
        if use:
            self.useLuceneCheckBox.setCheckState(2)
        else:
            self.useLuceneCheckBox.setCheckState(0)
            
    useLucene = property(_getUseLucene, _setUseLucene)
    
    def _getLuceneIndexUri(self):
        """
        Returns the lucene index uri.

        @return: The lucene index uri.
        @rtype: C{String}
        """
        return unicode(self.indexUriLineEdit.text())

    def _setLuceneIndexUri(self, uri):
        """
        Sets the lucene index uri.

        @param uri: The lucene index uri.
        @type uri: C{String}
        """
        self.indexUriLineEdit.setText(uri or "")
                
    luceneIndexUri = property(_getLuceneIndexUri, _setLuceneIndexUri)
    