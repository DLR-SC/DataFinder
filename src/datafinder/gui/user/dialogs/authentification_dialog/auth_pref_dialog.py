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

from datafinder.gui.user.dialogs.authentification_dialog.auth_edit_dialog import AuthEditDialogView

from datafinder.gui.gen.user.authentification_preferences_wizard_ui import Ui_auth_pref_dialog


__version__ = "$Revision-Id:$" 


class AuthPrefDialogView(QtGui.QDialog, Ui_auth_pref_dialog):
    """
    The dialog is displayed, when a user displays all of his stored authentification information. 
    Each connection can be opened to be edited.
    """

    def __init__(self, parent=None, preferences=None ):
        """
        Constructor.

        @param parent: Parent window of this L{QtGui.QDialog}
        @type parent: C{QtGui.QWidget}
        @param preferences: The preferences object.
        @type preferences: L{PreferencesHandler<datafinder.core.configuration.preferences.PreferencesHandler>}
        """

        QtGui.QDialog.__init__(self, parent)
        Ui_auth_pref_dialog.__init__(self)
       
        self.setupUi(self)
        
        self.useLdap = ""
        self.ldapBaseDn = ""
        self.ldapServerUri = ""
        self._preferences = preferences
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), self.reject)
        self.connect(self.okButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.editButton, QtCore.SIGNAL("clicked()"), self._editLocationActionSlot)
        
        # filling the gridbox with information about locations
        self.fillingTable(preferences.connectionUris)
        
                     
    def _editLocationActionSlot(self):
        """ Shows the edit Loaction dialog for more information on the location settings"""
        
        #Getting the currentRow with its Item and providing it as information to the EditView
        rowcount = self.authTable.currentRow()
        item = self.authTable.item(rowcount, 0)
        
        
        editDialog = AuthEditDialogView(None, self._preferences, item.text())
    
        if editDialog.exec_() == QtGui.QDialog.Accepted:
            print "good job"   
        
        
    def fillingTable(self, locations = None): 
        """ fills the table widget with information about authentification information """
        rowcount = 0
        
        if locations:
            for location in locations:
                #itemlocation = QtGui.QTableWidgetItem.setText(location)
                connection = self._preferences.getConnection(location)
                self.authTable.setItem(rowcount, 0, self.getNewTableWidget(location))
                # adding authmechanisminformation 
                # self.authTable.setItem(rowcount, 1, connection)
                self.authTable.setItem(rowcount, 2, self.getNewTableWidget(connection.username))
                self.authTable.setItem(rowcount, 3, self.getNewTableWidget(connection.password))
                # Adding ldap information 
                # self.authTable.setItem(rowcount, 4, connection)
                # Adding comment information 
                # self.authTable.setItem(rowcount, 5, connection)
                rowcount += 1            
    
    @staticmethod
    def getNewTableWidget(tableString):
        """ Creates the table widget. """
        
        widgetItem = QtGui.QTableWidgetItem()
        widgetItem.setText(tableString)
        
        return widgetItem
