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
Implements the principal search part of the privilege dialog.
"""


from PyQt4.QtGui import QMessageBox, QStandardItem, QStandardItemModel
from PyQt4.QtCore import QObject, SIGNAL

from datafinder.core.constants import SEARCH_MODE_GROUP_ONLY, \
                                      SEARCH_MODE_USER_AND_GROUP, SEARCH_MODE_USER_ONLY
from datafinder.core.item.privileges.principal import SPECIAL_PRINCIPALS
from datafinder.gui.user.common.util import startNewQtThread
from datafinder.gui.user.dialogs.privilege_dialog.items import PrincipalItem


__version__ = "$Revision-Id:$" 


class PrincipalSearchController(QObject):
    """ Handles the principal search interactions. """

    ADD_PRINCIPAL_SIGNAL = "addPrincipalSignal"
    
    def __init__(self, privilegeDialog, model):
        """ Constructor. 

        @param privilegeDialog: The privilege dialog.
        @type privilegeDialog: L{PrivilegeDialog<datafinder.gui.user.dialogs.privilege_dialog.main.PrivilegeDialog}
        @param model: The principal search model.
        @type model: L{<PrincipalSearchModel>datafinder.gui.user.dialogs.privilege_dialog.principal_search.PrincipalSearchModel} 
        """
        
        QObject.__init__(self)

        self._workerThread = None        
        self._privilegeDialog = privilegeDialog
        self._searchButton = privilegeDialog.principalSearchButton
        self._addPrincipalButton = privilegeDialog.addPrincipalButton
        self._searchEditor = privilegeDialog.principalSeachLineEdit
        self._bothFilterButton = privilegeDialog.bothFilterButton
        self._userFilterButton = privilegeDialog.userFilterButton
        self._groupFilterButton = privilegeDialog.groupFilterButton
        self._resultWidget = privilegeDialog.principalSearchResultWidget
        self._model = model
        self._messageBox = QMessageBox(QMessageBox.Critical, "Error during search", "", 
                                       QMessageBox.Ok, self._privilegeDialog)
        
        self._resultWidget.setModel(self._model)

        self.connect(self._searchButton, SIGNAL("clicked()"), self._searchSlot)
        self.connect(self._addPrincipalButton, SIGNAL("clicked()"), self._addPrincipalSlot)
        self.connect(self._resultWidget.selectionModel(), 
                     SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), 
                     self._selectionChangedSlot)
        
    def _searchSlot(self):
        """ Handles search requests. """
        
        pattern = unicode(self._searchEditor.text())
        searchMode = SEARCH_MODE_USER_AND_GROUP
        if self._userFilterButton.isChecked():
            searchMode = SEARCH_MODE_USER_ONLY
        elif self._groupFilterButton.isChecked():
            searchMode = SEARCH_MODE_GROUP_ONLY
        
        self._searchButton.setEnabled(False)
        self._resultWidget.setEnabled(False)
        self._workerThread = startNewQtThread(self._model.performPrincipalSearch,
                                              self._searchCallback,
                                              pattern, searchMode)    
        
    def _searchCallback(self):
        """ Handles errors and activates search button and result view again. """
        
        if not self._workerThread.error is None:
            self._messageBox.setText(self._workerThread.error.message)
            self._messageBox.show()
        self._searchButton.setEnabled(True)
        self._resultWidget.setEnabled(True)
        self._selectionChangedSlot()
        
    def _addPrincipalSlot(self):
        """ Determines selected principals and emits the corresponding signal. """
        
        items = list()
        for index in self._resultWidget.selectedIndexes():
            items.append(self._model.item(index.row()))
            
        self.emit(SIGNAL(self.ADD_PRINCIPAL_SIGNAL), items)

    def _selectionChangedSlot(self, _=None, __=None):
        """ Enables the add principal button if there are selected items. """
        
        self._addPrincipalButton.setEnabled(len(self._resultWidget.selectedIndexes()) > 0)


class PrincipalSearchModel(QStandardItemModel):
    """ Principal search model component. """
    
    def __init__(self, model):
        """ Constructor. 
        
        @param model: The repository model.
        @type model: L{<RepositoryModel>datafinder.gui.user.models.repository.repository.RepositoryModel} 
        """
        
        QStandardItemModel.__init__(self)
        
        self._model = model
        self._items = list()
        
        self._appendRows(SPECIAL_PRINCIPALS)
        
    def performPrincipalSearch(self, pattern, searchMode):
        """ Performs the search. 
        
        @param pattern: Name pattern.
        @type pattern: C{unicode}
        @type searchMode: Determines the search mode (user-only, group-only or both).
        @type searchMode: C{int}
        """

        principals = SPECIAL_PRINCIPALS + self._model.searchPrincipal(pattern, searchMode)
        self._appendRows(principals)
        
    def _appendRows(self, principals):
        """ Appends the principals to the internal model and clears it in advance. """
        
        self.clear()
        self._items = [PrincipalItem(principal) for principal in principals]
        for item in self._items:
            self.appendRow(item)

    def item(self, row, _=None):
        """ @see: L{item<PyQt4.QtGui.QStandardItemModel.item>} """

        try:
            item = self._items[row]
        except IndexError:
            item = QStandardItem()
        return item
