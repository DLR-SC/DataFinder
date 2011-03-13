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
Controls view displaying current content of a collection.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.user.common.controller import AbstractController
from datafinder.gui.user.common.delegate import AbstractDelegate
from datafinder.gui.user.common import util
        

__version__ = "$Revision-Id:$" 
        

class StackedCollectionsController(AbstractController):
    """
    Controls views displaying current content of a collection.
    """ 

    def __init__(self, stackedWidget, tableView, listView, viewsListAction, 
                 viewsTableAction, viewsIconsAction, mainWindow, parentController):
        """
        Constructor.
        """

        AbstractController.__init__(self, stackedWidget, mainWindow, None, True, parentController)

        self._tableController = _TableController(tableView, mainWindow, self)
        self._listController = _ListController(listView, mainWindow, self)
        listView.setUniformItemSizes(True)
        
        self.connect(viewsTableAction, QtCore.SIGNAL("triggered()"), self._viewsTableClickedSlot)
        self.connect(viewsListAction, QtCore.SIGNAL("triggered()"), self._viewsListClickedSlot)
        self.connect(viewsIconsAction, QtCore.SIGNAL("triggered()"), self._viewsIconClickedSlot)
        self.connect(self.widget, QtCore.SIGNAL("modelUpdateSignal"), self._modelUpdateSlot)

    def _viewsTableClickedSlot(self):
        """ Displays the table view. """

        self.setCurrentIndex(0)
        self._modelUpdateSlot(self.model)

    def _viewsListClickedSlot(self):
        """ Displays the list view. """

        self.setCurrentIndex(1)
        self._listController.setViewMode(QtGui.QListView.ListMode)
        self._modelUpdateSlot(self.model)

    def _viewsIconClickedSlot(self):
        """ Displays the icon view. """

        self.setCurrentIndex(1)
        self._listController.setViewMode(QtGui.QListView.IconMode)
        self._modelUpdateSlot(self.model)
        
    def _modelUpdateSlot(self, model):
        """ Slot is called when model data has changed. """

        self._listController.setSelectionModel(self._tableController.selectionModel())
        self._listController.itemActionController = self.parentController.itemActionController
        self._listController.model = model
        self._tableController.itemActionController = self.parentController.itemActionController
        self._tableController.model = model
        
    def focus(self):
        """ Sets focus to the current active view and selects the first item . """
        
        self._tableController.focus()

    def setEnabled(self, flag):
        """ Enables all controlled widgets. """
        
        self.widget.setEnabled(flag)
        self._listController.setEnabled(flag)      
        self._tableController.setEnabled(flag)
        
    @property
    def selectedIndexes(self):
        """ Returns the selected indexes. """
        
        return self._tableController.selectionModel().selectedRows()


class _TableController(AbstractController):
    """ Controls the table view displaying the items. """

    def __init__(self, tableView, mainWindow, parentController):
        """
        Constructor.
        """
        
        AbstractController.__init__(self, tableView, mainWindow, None, True, parentController)

        self.itemActionController = None
        self.model = None
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicator(0, QtCore.Qt.AscendingOrder)
        
        self._delegates = [_CollectionDelegate(self)]
        
    def focus(self):
        """ Sets focus to the current active view and selects the first item . """

        root = self.rootIndex()
        column = self.model.columnCount(root) - 1
        item = QtGui.QItemSelection(self.model.index(0, 0, root),
                                    self.model.index(0, column, root))
        self.selectionModel().clear()
        self.selectionModel().select(item, QtGui.QItemSelectionModel.Select)
        self.selectionModel().setCurrentIndex(self.model.index(0, 0, root),
                                              QtGui.QItemSelectionModel.Select)
        self.setFocus(QtCore.Qt.MouseFocusReason)

    
class _ListController(AbstractController):
    """ Controls icon and list view displaying items. """

    def __init__(self, listView, mainWindow, parentController):
        """
        Constructor.
        """

        AbstractController.__init__(self, listView, mainWindow, None, True, parentController)

        self.itemActionController = None
        self.model = None
        self._delegates = [_CollectionDelegate(self)]
    

class _CollectionDelegate(AbstractDelegate):
    """
    The Collection delegate manages a stacked collection view.
    """

    def __init__(self, controller):
        """
        Constructor.
        """
        
        AbstractDelegate.__init__(self, controller)
        
        self._itemDelegate = _CollectionItemDelegate(self)
        self._controller.setItemDelegate(self._itemDelegate)
        self.__itemActionController = None
        self.ignoreOpenAction = False

    @property
    def _selectionModel(self):
        """ Getter for the selection model. """

        return self._controller.widget.selectionModel()
        
    @property
    def _itemActionController(self):
        """ Getter for the ItemActionController. """
        
        self.__itemActionController.configure(self._controller.widget, list())
        return self.__itemActionController

    @util.immediateConnectionDecorator("widget", "modelUpdateSignal")
    def _modelSetSignalSlot(self, _):
        """ Reacts on changed model. """

        self.__itemActionController = self._controller.itemActionController
        self._itemDelegate.actionController = self._itemActionController
        
        QtCore.QObject.connect(self._selectionModel, 
                               QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
                               self._selectionChangedSlot) # ensures that _selectionChangedSlot is correctly connected
        
    @util.immediateConnectionDecorator("model", "updateSignal")
    def _modelUpdateSignalSlot(self, index):
        """ Reacts on data updates of the model. """

        self._controller.setRootIndex(self._controller.model.activeIndex)
        self._controller.selectionModel().clear()
        self._controller.selectionModel().select(index, QtGui.QItemSelectionModel.Select)
        self.__itemActionController.setItemActionEnabledState()
        
    @util.immediateConnectionDecorator("widget", "focusSignal")
    def _focusSignalSlot(self, isFocused):
        """ Slot is called when the widget is focused. """

        if isFocused:
            self._itemActionController.setItemActionEnabledState()

    def _selectionChangedSlot(self, _, __):
        """ Slot is called when the selection has changed and updates available item actions. """
        
        self._focusSignalSlot(self._controller.hasFocus())
        self._controller.mainWindow.statusBar().clearMessage()
        selectedRows = len(self._selectionModel.selectedRows())
        if selectedRows > 0:
            self._controller.mainWindow.statusBar().showMessage("%i items selected." % selectedRows)

    @util.immediateConnectionDecorator("widget", "doubleClicked(QModelIndex)")
    def _myWidgetDoubleClickedSlot(self, _):
        """ Slot is called when an item is double clicked in the list views. """

        self._openActionClickedSlot()
        
    @util.immediateConnectionDecorator("widget", "returnPressed")
    def _myWidgetReturnPressedSlot(self, _):
        """ Reacts on enter key hits on a specific item. """
        
        self._openActionClickedSlot()
        
    @util.deferredConnectionDecorator("selectAllAction", "triggered()")
    def _selectAllActionTriggeredSlot(self):
        """ Slot is called when all item in the current view has to be selected. """

        self._itemActionController.selectAllAction()

    @util.deferredConnectionDecorator("reverseSelectionAction", "triggered()")
    def _reverseSelectionActionTriggeredSlot(self):
        """ Inverts the current selection. """
        
        self._itemActionController.reverseSelectionAction()
            
    @util.immediateConnectionDecorator("widget", "customContextMenuRequested(QPoint)")
    def _customContextMenuRequestedSlot(self, _):
        """
        Shows the context menu at a valid position.
        """

        menu = self._itemActionController.createContextMenu(list())
        menu.exec_(QtGui.QCursor.pos())

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
        
    @util.deferredConnectionDecorator("pasteAction", "triggered()")
    def _pasteActionTriggeredSlot(self):
        """ Performs paste action. """

        self._itemActionController.pasteAction()
        
    @util.deferredConnectionDecorator("deleteAction", "triggered()")
    def _deleteActionTriggeredSlot(self):
        """ Performs delete action. """
        
        self._itemActionController.deleteAction()
                                
    @util.deferredConnectionDecorator("renameAction", "triggered()")
    def _renameActionTriggeredSlot(self):
        """ Performs rename action. """
        
        index = self._controller.selectionModel().currentIndex()
        if index.isValid():
            self._controller.edit(index)
        
    @util.deferredConnectionDecorator("createCollectionAction", "triggered()")
    def _createCollectionActionClickedSlot(self):
        """ Creates a new collection. """

        self._itemActionController.createCollection()
        
    @util.deferredConnectionDecorator("createLinkAction", "triggered()")
    def _createLinkActionClickedSlot(self):
        """ Creates a new link. """
        
        self._itemActionController.createLink()
    
    @util.deferredConnectionDecorator("createLeafAction", "triggered()")
    def _createLeafAction(self):
        """ Creates a leaf. """
        
        self._itemActionController.createLeaf()

    @util.deferredConnectionDecorator("importAction", "triggered()")
    def _importActionClickedSlot(self):
        """ Imports an item. """

        self._itemActionController.importAction()
    
    @util.deferredConnectionDecorator("exportAction", "triggered()")
    def _exportActionClickedSlot(self):
        """ Exports an item. """

        self._itemActionController.exportAction()
    
    @util.deferredConnectionDecorator("createArchiveAction", "triggered()")
    def _archiveActionClickedSlot(self):
        """ Archives an item. """

        self._itemActionController.createArchive()

    @util.deferredConnectionDecorator("editPropertiesAction", "triggered()")
    def _propertiesActionClickedSlot(self):
        """ Shows properties. """
        
        self._itemActionController.propertiesAction()

    @util.deferredConnectionDecorator("copyPropertiesAction", "triggered()")
    def _copyPropertiesActionClickedSlot(self):
        """ Initiates copying of properties. """
        
        self._itemActionController.prepareCopyPropertiesAction()

    @util.deferredConnectionDecorator("openAction", "triggered()")
    def _openActionClickedSlot(self):
        """ Opens the selected item. """
        
        if not self.ignoreOpenAction:
            self._itemActionController.openAction()
        
    @util.deferredConnectionDecorator("printAction", "triggered()")
    def _printActionClickedSlot(self):
        """ Prints the selected item. """

        self._itemActionController.printAction()
        
    @util.deferredConnectionDecorator("searchAction", "triggered()")
    def _searchActionClickedSlot(self):
        """ Opens the search dialog. """

        self._itemActionController.searchAction()

    @util.deferredConnectionDecorator("commitArchiveAction", "triggered()")
    def _commitArchiveActionClickedSlot(self):
        """ Commits changes of selected archives. """

        self._itemActionController.commitArchive()


class _CollectionItemDelegate(QtGui.QItemDelegate):
    """
    Controls the editing process of an item.
    """

    def __init__(self, collectionDelegate=None):
        """
        Constructor.
        """

        QtGui.QItemDelegate.__init__(self)
        self._collectionDelegate = collectionDelegate
        self.actionController = None
        
    def setEditorData(self, editor, index): # R201
        """
        @see: L{setEditorData<PyQt4.QtGui.QItemDelegate.setEditorData>}
        """

        data = index.model().data(index, QtCore.Qt.DisplayRole).toString()
        editor.setText(data)
        self._collectionDelegate.ignoreOpenAction = True
    
    def setModelData(self, editor, _, index):
        """
        @see: L{setEditorData<PyQt4.QtGui.QItemDelegate.setEditorData>}
        """

        try:
            if editor.isModified():
                newName = unicode(editor.text())
                self.actionController.renameAction(index, newName)
        finally:
            self._collectionDelegate.ignoreOpenAction = False
