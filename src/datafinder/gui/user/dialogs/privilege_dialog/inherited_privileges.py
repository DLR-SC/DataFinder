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
Implements handling of the inherited privileges of an item.
"""


__version__ = "$Revision-Id:$" 


from PyQt4.QtGui import QItemSelection, QItemSelectionModel, QStandardItemModel
from PyQt4.QtCore import QObject, SIGNAL

from datafinder.gui.user.dialogs.privilege_dialog.items import AccessLevelItem, PrincipalItem


class InheritedPrivilegeController(QObject):
    """ Implements privilege handling related interactions. """
    
    def __init__(self, privilegeDialog, repositoryModel, model):
        """ Constructor. """

        QObject.__init__(self)
        
        self._editButton = privilegeDialog.editButton
        self._privilegeWidget = privilegeDialog.inheritedPrivilegeTable
        self._selectItemWidget = privilegeDialog.selectItemWidget
        self._model = model
        self._repositoryModel = repositoryModel
        
        self._privilegeWidget.setModel(self._model)
        
        self.connect(self._privilegeWidget.selectionModel(), 
                     SIGNAL("currentRowChanged(QModelIndex, QModelIndex)"),
                     self._privilegeSelectionChanged)
        self.connect(self._selectItemWidget, 
                     SIGNAL(self._selectItemWidget.SELECTED_INDEX_CHANGED_SIGNAL),
                     self._itemWidgetSelectionChanged)
        self.connect(self._editButton, SIGNAL("clicked()"), self._editClicked)
        
    def _privilegeSelectionChanged(self, currentIndex, _):
        """ Handles changes of the privilege table selection. """
        
        if currentIndex.isValid():
            item = self._model.determinePrivilegeSource(currentIndex.row())
            index = self._repositoryModel.indexFromPath(item.path)
            self._selectItemWidget.selectedIndex = index
            
    def _itemWidgetSelectionChanged(self, index):
        """ Handles changed items of the select item widget and
        selects corresponding privilege definition in the table. """
        
        item = self._repositoryModel.nodeFromIndex(index)
        rows = self._model.determineRows(item)
        topLeft = self._model.index(rows[0], 0)
        bottomRight = self._model.index(rows[len(rows )- 1], 3)
        selection = QItemSelection(topLeft, bottomRight)
        self._privilegeWidget.selectionModel().clearSelection()
        self._privilegeWidget.selectionModel().setCurrentIndex(topLeft, QItemSelectionModel.Select)     
        self._privilegeWidget.selectionModel().select(selection, QItemSelectionModel.Select)
            
    def _editClicked(self):
        """ Handles the editing of the new item. """
            
        item = self._repositoryModel.nodeFromIndex(self._selectItemWidget.selectedIndex)
        self._privilegeWidget.item = item
            
    def _setItem(self, item):
        """ Sets the item. """
        
        self._model.item_ = item
        self._selectItemWidget.showPathEditor()
        index = self._repositoryModel.indexFromPath("/")
        self._selectItemWidget.selectedIndex = index
        self._itemWidgetSelectionChanged(index)
        
    item = property(None, _setItem)


class InheritedPrivilegeModel(QStandardItemModel):
    """ Implements the model for inherited privileges. """

    def __init__(self):
        """ Constructor. """
        
        QStandardItemModel.__init__(self)
        
        self._rowItemMap = dict()
        self._itemRowMap = dict()
        self.setColumnCount(4) # principal, content, properties, administration

    def _setItem(self, item):
        """ Sets the item. """
        
        # Determines all parent items
        items = list()
        currentItem = item.parent
        while not currentItem is None:
            items.append(currentItem)
            currentItem = currentItem.parent
        items.reverse()
        
        # Add the items to the internal model
        for item in items:
            self._itemRowMap[item.path] = list()
            for principal in item.acl.principals:
                currentRow = self.rowCount()
                self._rowItemMap[currentRow] = item
                self._itemRowMap[item.path].append(currentRow)
                row = [PrincipalItem(principal)]
                row[0].item = item
                row.append(AccessLevelItem(item.acl.contentAccessLevel(principal).displayName, True))
                row.append(AccessLevelItem(item.acl.propertiesAccessLevel(principal).displayName, True))
                row.append(AccessLevelItem(item.acl.administrationAccessLevel(principal).displayName, True)) 
                self.appendRow(row)

    item_ = property(None, _setItem) # item already exists as method

    def determinePrivilegeSource(self, row):
        """ Returns the item which belongs to the given row.
        
        @param row: The row number.
        @type row: C{int}
        
        @return: The item that corresponds to the privilege definition in the given row. 
        @rtype: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        return self._rowItemMap[row]

    def determineRows(self, item):
        """ Determines all row number to which the item belongs.
        
        @param item: The requested item.
        @rtype: L{ItemBase<datafinder.core.item.base.ItemBase>}
        
        @return: Corresponding privilege rows.
        @rtype: C{list} of C{int}
        """
        
        return self._itemRowMap[item.path]
