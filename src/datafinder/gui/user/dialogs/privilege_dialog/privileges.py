#
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
Implements privilege handling.
"""


from copy import deepcopy

from PyQt4.QtGui import QStandardItemModel, QDialogButtonBox
from PyQt4.QtCore import QObject, SIGNAL

from datafinder.gui.user.dialogs.privilege_dialog.items import AccessLevelItem, PrincipalItem


__version__ = "$Revision-Id:$" 


class PrivilegeController(QObject):
    """ Implements privilege handling related interactions. """
    
    def __init__(self, privilegeDialog, model):
        """ Constructor. """

        QObject.__init__(self)
        
        self._applyButton = privilegeDialog.buttonBox.button(QDialogButtonBox.Apply)
        self._removeButton = privilegeDialog.removePrincipalButton
        self._upButton = privilegeDialog.upButton
        self._downButton = privilegeDialog.downButton
        self._privilegeWidget = privilegeDialog.privilegeTable
        self._model = model
        
        self._privilegeWidget.setModel(self._model)
        
        self.connect(self._removeButton, SIGNAL("clicked()"), self._removePrincipalsSlot)

    def _setItem(self, item):
        """ Sets the item. """
        
        self._applyButton.setEnabled(False)
        self._model.item_ = item
    item = property(None, _setItem)
    
    def addPrincipals(self, principals):
        """ @see: L{PrivilegeModel.addPrincipals<datafinder.gui.user.dialogs.
        privilege_dialog.privileges.PrivilegeModel.addPrincipals>}
        in addition it enables or disables the apply button.
        """
        
        self._model.addPrincipals(principals)
        self._applyButton.setEnabled(self._model.isDirty)
        
    def _removePrincipalsSlot(self):
        """ Remove the selected principals. """
        
        principals = list()
        rows = list()  # to avoid multiple entries
        for index in self._privilegeWidget.selectedIndexes():
            item = self._model.item(index.row(), 0)
            if not index.row() in rows:
                principals.append(item)
                rows.append(index.row())
            
        self._model.removePrincipals(principals)
        self._applyButton.setEnabled(self._model.isDirty)

        
class PrivilegeModel(QStandardItemModel):
    """ Implements the privilege model. """
    
    def __init__(self, model):
        """ Constructor. """
        
        QStandardItemModel.__init__(self)
        
        self._model = model
        self._item = None
        self._acl = None
        
        self.setColumnCount(4) # principal, content, properties, administration
    
    def _setItem(self, item):
        """ Sets the item. """
        
        self._item = item
        self._acl = deepcopy(item.acl)
 
        self.clear()
        for principal in self._acl.principals:
            self._appendRow(principal)
    item_ = property(None, _setItem) # item already exists as method
    
    @property
    def isDirty(self):
        """ Checks whether the model contains not stored changes.
        
        @return: C{True} if there are those changes else C{False}.
        @rtype: C{bool}
        """
        
        return self._acl != self._item.acl
    
    def addPrincipals(self, principalItems):
        """ Adds the given principals with default access level. 
        
        @param principalItems: Principals which should be added.
        @type principalItems: C{list} of  L{PrincipalItem<datafinder.gui.user.
        dialogs.privilege_dialog.items.PrincipalItem>}
        """
        
        for principalItem in principalItems:
            principal = principalItem.principal
            if not principal in self._acl.principals:
                self._acl.addDefaultPrincipal(principal)
                self._appendRow(principal)
                
    def _appendRow(self, principal):
        """ Adds the principal and its access levels to the table view. """
       
        row = [PrincipalItem(principal)]
        row.append(AccessLevelItem(self._acl.contentAccessLevel(principal)))
        row.append(AccessLevelItem(self._acl.propertiestAccessLevel(principal)))
        row.append(AccessLevelItem(self._acl.aministrationAccessLevel(principal)))
        self.appendRow(row)
        
    def removePrincipals(self, principalItems):
        """ Removes the specified principals from the ACL.
        
        @param principalItems: List of principals to remove.
        @type principalItems: C{list} of L{PrincipalItem<datafinder.gui.user.
        dialogs.privilege_dialog.items.PrincipalItem>}
        """
        
        principalItems.reverse()
        for principalItem in principalItems:
            self._acl.clearPrivileges(principalItem.principal)
            self.removeRow(principalItem.row())
