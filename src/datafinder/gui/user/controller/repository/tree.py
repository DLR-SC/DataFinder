# pylint: disable=R0201
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#
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
Controls the tree view of collections.
"""


from PyQt4 import QtGui, QtCore

from datafinder.gui.user.common.delegate import AbstractDelegate
from datafinder.gui.user.common.controller import AbstractController
from datafinder.gui.user.common import util
from datafinder.gui.user.controller.constants import SELECT_ALL_ACTION, PRINT_ACTION, \
                                                     REVERSE_SELECTION, OPEN_ACTION
                                                     


__version__ = "$Revision-Id:$" 


class TreeController(AbstractController):
    """
    Controls the tree view of collections.
    """

    def __init__(self, treeView, mainWindow, parentController):
        """
        Constructor.
        """

        AbstractController.__init__(self, treeView, mainWindow, None, True, parentController)

        treeView.setUniformRowHeights(True)
        self._delegates = [_TreeDelegate(self)]
        
    @property
    def itemActionController(self):
        """ Creates the ItemActionController bound to the tree view. """
        
        return self.parentController.itemActionController
        

class _TreeDelegate(AbstractDelegate):
    """
    Controls the tree view.
    """

    _DISABLED_ACTIONS = [SELECT_ALL_ACTION, REVERSE_SELECTION, OPEN_ACTION, PRINT_ACTION]
    
    def __init__(self, controller):
        """
        Constructor.
        """

        AbstractDelegate.__init__(self, controller)
        self.__itemActionController = None
        self._itemDelegate = _TreeItemDelegate(self._controller.mainWindow)
        self._controller.setItemDelegate(self._itemDelegate)

    @property
    def _itemActionController(self):
        """ Getter for the ItemActionController. """
        
        self.__itemActionController.configure(self._controller.widget, self._DISABLED_ACTIONS)
        return self.__itemActionController
    
    @util.immediateConnectionDecorator("model", "updateSignal")
    def _modelUpdateSignalSlot(self, _):
        """ Reacts on data updates. """

        self._controller.scrollTo(self._controller.model.activeIndex)
        self._controller.clearSelection()
        self._controller.selectionModel().setCurrentIndex(self._controller.model.activeIndex, QtGui.QItemSelectionModel.Select)

    @util.immediateConnectionDecorator("widget", "modelUpdateSignal")
    def _modelSetSignalSlot(self, _):
        """ Reacts on changes of the model. """
        
        self.__itemActionController = self._controller.itemActionController
        self._itemDelegate.actionController = self._itemActionController

    @staticmethod
    @util.immediateConnectionDecorator(["serverTreeSelectionModel", "localTreeSelectionModel"],
                                        "currentChanged(QModelIndex, QModelIndex)")
    def _currentIndexChangedSlot(index):
        """ Slot is called when an item is selected in the tree view. """
        
        if index.isValid():
            if index.model().activeIndex != index:
                index.model().activeIndex = index
    
    @util.deferredConnectionDecorator(["serverTreeSelectionModel", "localTreeSelectionModel"], 
                                       "selectionChanged(QItemSelection, QItemSelection)")
    def _selectionChangedSlot(self, _, __):
        """ Slot is called when the selection has changed and updates available item actions. """

        self._itemActionController.setItemActionEnabledState()
        
    @util.immediateConnectionDecorator("widget", "focusSignal")
    def _focusSignalSlot(self, isFocused):
        """ Slot is called when the widget is focused. """

        if isFocused:
            self._itemActionController.setItemActionEnabledState()
    
    @util.immediateConnectionDecorator("widget", "clicked(QModelIndex)")
    def _toggleExpandActionSlot(self, index):
        """ Toggles the file menu action between the expand and collapse action. """

        self._setExpansionState(index)

    def _setExpansionState(self, index):
        """ Sets the expansion state. """
        
        visible = self._controller.isExpanded(index)
        self._mainWindow.expandAction.setVisible(not visible)
        self._mainWindow.collapseAction.setVisible(visible)

    @util.deferredConnectionDecorator("expandAction", "triggered()")
    def _expandActionTriggeredSlot(self):
        """ Slot is called when the extend action was triggered. """

        index = self._controller.selectionModel().currentIndex()
        self._controller.expand(index)
        self._setExpansionState(index)

    @util.deferredConnectionDecorator("collapseAction", "triggered()")
    def _collapseActionTriggeredSlot(self):
        """ Slot is called when the collapse action was triggered. """

        index = self._controller.selectionModel().currentIndex()
        self._controller.collapse(index)
        self._setExpansionState(index)

    @util.immediateConnectionDecorator("widget", "customContextMenuRequested(QPoint)")
    def _customContextMenuRequestedSlot(self, _):
        """ Shows the context menu at a valid position. """
        
        menu = self._itemActionController.createContextMenu(self._DISABLED_ACTIONS,
                                                            [self._controller.mainWindow.expandAction, 
                                                             self._controller.mainWindow.collapseAction])
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

    @util.deferredConnectionDecorator("searchAction", "triggered()")
    def _searchActionClickedSlot(self):
        """ Opens the search dialog. """

        self._itemActionController.searchAction()

    @util.deferredConnectionDecorator("commitArchiveAction", "triggered()")
    def _commitArchiveActionClickedSlot(self):
        """ Commits changes of selected archives. """

        self._itemActionController.commitArchive()


class _TreeItemDelegate(QtGui.QItemDelegate):
    """
    Controls the editing process of a tree item.
    """

    def __init__(self, parent=None):
        """
        Constructor.

        @param parent: Parent object of the delegate.
        @type parent: L{QObject<PyQt4.QtCore.QObject>}
        """

        QtGui.QItemDelegate.__init__(self, parent)
        self.actionController = None

    def setEditorData(self, editor, index): # R0201
        """
        @see: L{setEditorData<PyQt4.QtGui.QItemDelegate.setEditorData>}
        """

        data = index.model().data(index, QtCore.Qt.DisplayRole).toString()
        editor.setText(data)
    
    def setModelData(self, editor, _, index):
        """
        @see: L{setEditorData<PyQt4.QtGui.QItemDelegate.setEditorData>}
        """

        if editor.isModified():
            newName = unicode(editor.text())
            self.actionController.renameAction(index, newName)
