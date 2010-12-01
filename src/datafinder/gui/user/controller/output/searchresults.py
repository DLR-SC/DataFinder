# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
#
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
Implements output area for search results.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.user.common import util
from datafinder.gui.user.common.delegate import AbstractDelegate
from datafinder.gui.user.common.controller import AbstractController
from datafinder.gui.user.controller.constants import CREATE_ARCHIVE_ACTION, CREATE_COLLECTION_ACTION, \
                                                     CREATE_LEAF_ACTION, CREATE_LINK_ACTION, RENAME_ACTION


__version__ = "$Revision-Id:$" 


class SearchResultController(AbstractController):
    """
    Controls view displaying search results.
    """

    def __init__(self, tableView, mainWindow, parentController, itemActionController):
        """ Constructor. """

        AbstractController.__init__(self, tableView, mainWindow, None, True, parentController)
        self.horizontalHeader().setSortIndicator(0, QtCore.Qt.AscendingOrder)

        self._delegates = [_SearchResultDelegate(self, itemActionController)]


class _SearchResultDelegate(AbstractDelegate):
    """
    Handles signals of the search result view.
    """

    _DISABLED_ACTIONS = [CREATE_ARCHIVE_ACTION, CREATE_COLLECTION_ACTION, 
                         CREATE_LEAF_ACTION, CREATE_LINK_ACTION, RENAME_ACTION]
    
    def __init__(self, controller, itemActionController):
        """
        Constructor.
        """

        AbstractDelegate.__init__(self, controller)
        self._widgetDoubleClickedSlot = None
        self.__itemActionController = itemActionController

    @property
    def _selectionModel(self):
        """ Getter for the selection model. """
        
        return self._controller.widget.selectionModel()

    @property
    def _itemActionController(self):
        """ Getter for the ItemActionController. """
        
        self.__itemActionController.configure(self._controller.widget, self._DISABLED_ACTIONS)
        return self.__itemActionController
    
    @util.immediateConnectionDecorator("model", "updateSignal")
    def _modelUpdatedSlot(self):
        """ Slot is called when the model data was updated. """

        self._controller.setEnabled(self._controller.model.rowCount() > 0)
        self._controller.widget.setRootIndex(QtCore.QModelIndex())

    @util.immediateConnectionDecorator("widget", "modelUpdateSignal")
    def _modelChangedSlot(self, _):
        """ Slot is called when the model has changed. """
        
        self._controller.setSortingEnabled(True)
        
    @util.immediateConnectionDecorator("widget", "focusSignal")
    def _focusSignalSlot(self, isFocused):
        """ Slot is called when the widget is focused. """

        if isFocused:
            self._itemActionController.setItemActionEnabledState()
    
    @util.immediateConnectionDecorator("_selectionModel", "selectionChanged(QItemSelection, QItemSelection)")
    def _selectionChangedSlot(self, _, __):
        """ Slot is called when the selection has changed and updates available item actions. """
        
        self._focusSignalSlot(self._controller.hasFocus())
        self._controller.mainWindow.statusBar().clearMessage()
        selectedRows = len(self._selectionModel.selectedRows())
        if selectedRows > 0:
            self._controller.mainWindow.statusBar().showMessage("%i items selected." % selectedRows)
    
    @util.immediateConnectionDecorator("widget", "doubleClicked(QModelIndex)")
    def _doubleClickSlot(self, index):
        """ Handles the double click event on an item. """
        
        self._controller.model.activeIndex = index
        
    @util.immediateConnectionDecorator("widget", "customContextMenuRequested(QPoint)")
    def _showContextMenuSlot(self, pos):
        """ Shows the context menu at a valid position. """

        if self._controller.indexAt(pos).isValid():
            menu = self._itemActionController.createContextMenu(self._DISABLED_ACTIONS)
            action = menu.addAction(menu.tr("Clear"))
            action.connect(action, QtCore.SIGNAL("triggered()"), self._controller.model.clear)
            menu.exec_(QtGui.QCursor.pos())

    @util.deferredConnectionDecorator("editPropertiesAction", "triggered()")
    def _propertiesActionClickedSlot(self):
        """ Shows properties. """
        
        self._itemActionController.propertiesAction()
        
    @util.deferredConnectionDecorator("copyAction", "triggered()")
    def _copyActionTriggeredSlot(self):
        """ Prepares a copy action. """

        self._itemActionController.prepareCopyAction()
        
    @util.deferredConnectionDecorator("copyPropertiesAction", "triggered()")
    def _copyPropertiesActionSlot(self):
        """ Prepares copying of properties. """
        
        self._itemActionController.prepareCopyPropertiesAction()
        
    @util.deferredConnectionDecorator("cutAction", "triggered()")
    def _cutActionTriggeredSlot(self):
        """ Prepares cut action. """

        self._itemActionController.prepareCutAction()

    @util.deferredConnectionDecorator("deleteAction", "triggered()")
    def _deleteActionTriggeredSlot(self):
        """ Performs delete action. """
        
        self._itemActionController.deleteAction(QtCore.QModelIndex())
        
    @util.deferredConnectionDecorator("selectAllAction", "triggered()")
    def _selectAllActionTriggeredSlot(self):
        """ Slot is called when all item in the current view has to be selected. """

        self._itemActionController.selectAllAction()

    @util.deferredConnectionDecorator("reverseSelectionAction", "triggered()")
    def _reverseSelectionActionTriggeredSlot(self):
        """ Inverts the current selection. """
        
        self._itemActionController.reverseSelectionAction()

    @util.deferredConnectionDecorator("openAction", "triggered()")
    def _openActionClickedSlot(self):
        """ Opens the selected item. """
        
        self._itemActionController.openAction()
        
    @util.deferredConnectionDecorator("printAction", "triggered()")
    def _printActionClickedSlot(self):
        """ Prints the selected item. """

        self._itemActionController.printAction()

    @util.deferredConnectionDecorator("importAction", "triggered()")
    def _importActionClickedSlot(self):
        """ Imports an item. """

        self._itemActionController.importAction()
    
    @util.deferredConnectionDecorator("exportAction", "triggered()")
    def _exportActionClickedSlot(self):
        """ Exports an item. """

        self._itemActionController.exportAction()

    @util.deferredConnectionDecorator("searchAction", "triggered()")
    def _searchActionClickedSlot(self):
        """ Opens the search dialog. """

        self._itemActionController.searchAction()

    @util.deferredConnectionDecorator("commitArchiveAction", "triggered()")
    def _commitArchiveActionClickedSlot(self):
        """ Commits changes of selected archives. """

        self._itemActionController.commitArchive()
