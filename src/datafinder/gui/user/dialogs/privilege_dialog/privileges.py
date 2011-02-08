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

from PyQt4.QtGui import QStandardItemModel, QDialogButtonBox, QMessageBox, QStyledItemDelegate
from PyQt4.QtCore import QObject, SIGNAL

from datafinder.core.item.privileges.privilege import ACCESS_LEVELS
from datafinder.gui.user.common.util import startNewQtThread
from datafinder.gui.user.dialogs.privilege_dialog.items import AccessLevelItem, PrincipalItem


__version__ = "$Revision-Id$" 


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
        self._workerThread = None
        self._messageBox = QMessageBox(QMessageBox.Critical, "Error during privilege storage", "", 
                                       QMessageBox.Ok, privilegeDialog)
        
        
        self._privilegeWidget.setModel(self._model)
        self._setButtonEnabledState(False)
        self._privilegeWidget.setItemDelegate(_AccessLevelItemDelegate(self, self._model))
        
        self.connect(self._applyButton, SIGNAL("clicked()"), self.applySlot)
        self.connect(self._removeButton, SIGNAL("clicked()"), self._removePrincipalsSlot)
        self.connect(self._upButton, SIGNAL("clicked()"), self._createMoveRowSlot(-1))
        self.connect(self._downButton, SIGNAL("clicked()"), self._createMoveRowSlot(1))
        self.connect(self._privilegeWidget.selectionModel(), 
                     SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
                     self._selectionChangedSlot)
        
    def _setButtonEnabledState(self, enabled):
        """ Sets the enabled state for all controlled buttons. """
        
        self._applyButton.setEnabled(enabled)
        self._removeButton.setEnabled(enabled)
        self._upButton.setEnabled(enabled)
        self._downButton.setEnabled(enabled)
         
    def checkApplyEnabledState(self):
        """ checks whether the apply button has to be activated which is only
        required if the model contains unsaved changes. """
        
        self._applyButton.setEnabled(self._model.isDirty)

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
        self.checkApplyEnabledState()
        
    def applySlot(self):
        """ Initializes the ACL update in separated thread. 
        This is only performed if the model contains unsaved changes. """
        
        if self._model.isDirty:
            self._setButtonEnabledState(False)
            self._privilegeWidget.setEnabled(False)
            self._workerThread = startNewQtThread(self._model.store, self._applyCallback)
        
    def _applyCallback(self):
        """ Checks the thread result and enables the dialog elements again. """
        
        if not self._workerThread.error is None:
            self._messageBox.setText(self._workerThread.error.message)
            self._messageBox.show()
        
        self._privilegeWidget.setEnabled(True)
        self._privilegeWidget.selectionModel().clearSelection()
        
    def _removePrincipalsSlot(self):
        """ Remove the selected principals. """
        
        self._model.removePrincipals(self._determinePrincipalItems())
        self.checkApplyEnabledState()
        
    def _createMoveRowSlot(self, posDiff):
        """ Creates a slot used for moving a whole principal row. """
        
        def _moveRowSlot():
            """ Handles the row moving. """
            
            principalItem = self._determinePrincipalItems()[0]
            newRow = principalItem.row() + posDiff
            self._model.movePrincipalPosition(principalItem, newRow)
            self.checkApplyEnabledState()
            self._privilegeWidget.selectRow(newRow)
        return _moveRowSlot
        
    def _determinePrincipalItems(self):
        """ Determines the selected principal items. """
        
        principals = list()
        rows = list()  # used to check for / avoid multiple entries
        for index in self._privilegeWidget.selectedIndexes():
            item = self._model.item(index.row(), 0)
            if not index.row() in rows:
                principals.append(item)
                rows.append(index.row())
        return principals
        
    def _selectionChangedSlot(self, _, __):
        """ Handles button enabling states in accordance to the selected items. """
        
        principals = self._determinePrincipalItems()
        self._removeButton.setEnabled(True)
        self._upButton.setEnabled(False)
        self._downButton.setEnabled(False)
            
        if len(principals) == 1:
            self._upButton.setEnabled(principals[0].row() > 0)
            self._downButton.setEnabled(principals[0].row() < self._model.rowCount() - 1)
        elif len(principals) == 0:
            self._removeButton.setEnabled(False)


class _AccessLevelItemDelegate(QStyledItemDelegate):
    """ Implements an item delegate to provide a suitable editor (combination box)
    for changing access level values. """

    def __init__(self, controller, model, parent=None):
        """
        Constructor.
        """

        QStyledItemDelegate.__init__(self, parent)
        self._controller = controller
        self._model = model
        
    def createEditor(self, parent, _, index):
        """ @see: L{createEditor<PyQt4.QtGui.QItemDelegate.createEditor>} """

        if index.isValid():
            item = self._model.item(index.row(), index.column())
            if index.column() > 0:
                return item.createEditor(parent)
            
    def setModelData(self, editor, _, index):
        """ @see: L{setModelData<PyQt4.QtGui.QItemDelegate.setModelData>} """
        
        if index.isValid():
            levelName = editor.currentText()
            item = self._model.item(index.row(), index.column())
            self._model.changeAccessLevel(item, levelName)
            self._controller.checkApplyEnabledState()


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
        row.append(AccessLevelItem(self._acl.contentAccessLevel(principal).displayName))
        row.append(AccessLevelItem(self._acl.propertiesAccessLevel(principal).displayName))
        row.append(AccessLevelItem(self._acl.administrationAccessLevel(principal).displayName)) 
        self.appendRow(row)
        
    def removePrincipals(self, principalItems):
        """ Removes the specified principals from the ACL.
        
        @param principalItems: List of principals to remove.
        @type principalItems: C{list} of L{PrincipalItem<datafinder.gui.user.
        dialogs.privilege_dialog.items.PrincipalItem>}
        """
        
        principalItems.reverse()
        for principalItem in principalItems:
            if principalItem.principal in self._acl.principals:
                self._acl.clearPrivileges(principalItem.principal)
                self.removeRow(principalItem.row())
            
    def movePrincipalPosition(self, principalItem, newRow):
        """
        Moves the principal row to the new position.
        
        @param principalItem: Principal to move.
        @type principalItem: L{PrincipalItem<datafinder.gui.user.
        dialogs.privilege_dialog.items.PrincipalItem>}
        @param newRow: The new row position.
        @type newRow: C{int}
        """
        
        if principalItem.principal in self._acl.principals:
            self._acl.setIndex(principalItem.principal, newRow)
            items = self.takeRow(principalItem.row())
            self.insertRow(newRow, items)

    def store(self):
        """ Stores the current ACL state. """
        
        self._item.updateAcl(self._acl)
        self._acl = deepcopy(self._acl)
        
    def changeAccessLevel(self, levelItem, levelName):
        """ Changes the associated access level. Also the data model 
        is adapted in accordance.

        @param principalItem: Principal to move.
        @type principalItem: L{AccessLevelItem<datafinder.gui.user.
        dialogs.privilege_dialog.items.AccessLevelItem>}
        @param levelName: The new access level display name.
        @type levelName: C{unicode}
        """
        
        principal = self.item(levelItem.row()).principal
        if principal in self._acl.principals:
            level = None
            for accessLevel in ACCESS_LEVELS:
                if levelName == accessLevel.displayName:
                    level = accessLevel
                    break
            if not level is None:
                levelItem.setText(levelName)
                if levelItem.column() == 1:
                    self._acl.setContentAccessLevel(principal, level)
                elif levelItem.column() == 2:
                    self._acl.setPropertiesAccessLevel(principal, level)
                elif levelItem.column() == 3:
                    self._acl.setAdministrationAccessLevel(principal, level)
