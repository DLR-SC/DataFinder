# pylint: disable=W0142
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
Implements handling of item-specific actions.
"""


import logging
import sys

from PyQt4 import QtCore, QtGui

from datafinder.core.item.data_persister.constants import ITEM_STATE_ARCHIVED, ITEM_STATE_ARCHIVED_READONLY
from datafinder.gui.user.constants import LOGGER_ROOT
from datafinder.gui.user.common.progress_dialog import ProgressDialog
from datafinder.gui.user.controller import constants as ac
from datafinder.gui.user.dialogs.creation_wizard import CreationWizard
from datafinder.gui.user.dialogs.properties_dialog import PropertiesDialog
from datafinder.gui.user.dialogs.search_dialog import SearchDialog
from datafinder.gui.user.models import constants
from datafinder.gui.user.models.properties import PropertiesModel


__version__ = "$Revision-Id:$" 


class ItemActionController(object):
    """
    Implements handling of item-specific actions.
    """

    _logger = logging.getLogger(LOGGER_ROOT)
    
    def __init__(self, mainWindow, sourceRepositoryModel, targetRepositoryModel, scriptController):
        """
        Constructor.
        
        @param mainWindow: MainWindow reference.
        @type mainWindow: L{MainWindow<datafinder.gui.user.application.MainWindow>}
        @param sourceRepositoryModel: The source repository model.
        @type sourceRepositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.repositoryRepositoryModel>}
        @param targetRepositoryModel: The target repository model.
        @type targetRepositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>}
        @param scriptController: The script controller component used to get access to registered script extensions.
        @type scriptController: L{ScriptController<datafinder.gui.user.controller.scripts.ScriptController>}
        """
        
        self._mainWindow = mainWindow
        self._sourceRepositoryModel = sourceRepositoryModel
        self._targetRepositoryModel = targetRepositoryModel
        self._scriptController = scriptController
        self._widget = None
        self._disabledActions = list()
        
        self._creationWizard = None
        self._progressDialog = None
        self._searchDialog = None

        self._itemActionChecker = _ItemActionChecker(self._sourceRepositoryModel,
                                                     self._targetRepositoryModel,
                                                     self._scriptController)

    def configure(self, widget, disabledActions):
        """ 
        Sets the currently used widget and the general disabled actions.
        
        @param widget: The item widget that is currently controlled.
        @type widget: L{QAbstractItemView<PyQt4.QtGui.QAbstractItemView>}
        @param disabledActions: List of general disabled action constants.
        @type disabledActions: C{list} of C{unicode}  
        """
        
        self._widget = widget
        self._disabledActions = disabledActions
         
    def prepareCopyAction(self):
        """ Notes the currently selected items for copying. """

        selectedIndexes = self._determineSelectedIndexes()
        if len(selectedIndexes) > 0:
            self._sourceRepositoryModel.clipboard.setCopyIndexes(selectedIndexes)
            self._mainWindow.pasteAction.setEnabled(True)
            
    def prepareCutAction(self):
        """ Notes the currently selected items for moving. """
        
        selectedIndexes = self._determineSelectedIndexes()
        if len(selectedIndexes) > 0:
            self._sourceRepositoryModel.clipboard.setCutIndexes(selectedIndexes)
            self._mainWindow.pasteAction.setEnabled(True)

    def prepareCopyPropertiesAction(self):
        """ Notes the currently selected item as source for property copying action. """

        selectedIndexes = self._determineSelectedIndexes()
        if len(selectedIndexes) == 1:
            self._sourceRepositoryModel.clipboard.setCopyPropertiesIndex(selectedIndexes[0])
            self._mainWindow.pasteAction.setEnabled(True)

    def _determineSelectedIndexes(self):
        """ 
        Determines the selected indexes and ensures that 
        for a row only the first index is in the returned result. 
        """

        selectedIndexes = list()
        if len(self._selectionModel.selectedRows()) > 0:
            for index in self._selectionModel.selectedRows():
                selectedIndexes.append(self._mapIndexToSource(index))
        selectedIndexes = sorted(selectedIndexes, cmp=lambda x, y: cmp(x.row(), y.row()), reverse=True)
        return selectedIndexes
    
    def pasteAction(self):
        """ Performs paste action, e.g. copying of items. The target is the current selected directory. """

        clipboard = self._sourceRepositoryModel.clipboard
        targetIndex = self._sourceRepositoryModel.activeIndex
        selectedIndexes = self._determineSelectedIndexes()
        if len(selectedIndexes) == 1 \
           and clipboard.state == constants.CLIPBOARD_STATE_COPY_PROPERTIES:
            targetIndex = selectedIndexes[0]
        targetIndex = self._mapIndexToSource(targetIndex)
        indexes = clipboard.indexes
        if len(indexes) > 0:
            def pasteCallback():
                self._sourceRepositoryModel.activeIndex = self._sourceRepositoryModel.activeIndex
            if clipboard.state == constants.CLIPBOARD_STATE_COPY:
                self._sourceRepositoryModel.lock([targetIndex])
                def copyCallback():
                    self._sourceRepositoryModel.unlock(targetIndex)
                    self._sourceRepositoryModel.activeIndex = targetIndex
                self._performWithProgressDialog("Copy", "Copying items...", copyCallback,
                                                self._sourceRepositoryModel.copy, indexes, targetIndex)
            elif clipboard.state == constants.CLIPBOARD_STATE_CUT:
                parents = [targetIndex]
                for index in indexes:
                    parents.append(index.parent())
                self.__invalidateFilterModel()
                self._sourceRepositoryModel.lock(parents)
                def cutCallback():
                    self.__invalidateFilterModel()
                    for index in parents:
                        self._sourceRepositoryModel.unlock(index)
                    self._sourceRepositoryModel.activeIndex = targetIndex
                self._performWithProgressDialog("Move", "Moving items...", cutCallback,
                                                self._sourceRepositoryModel.move, indexes, targetIndex)
            elif clipboard.state == constants.CLIPBOARD_STATE_COPY_PROPERTIES:
                self._performWithProgressDialog("Copy Properties", "Copying properties...", pasteCallback,
                                                self._sourceRepositoryModel.copyProperties, indexes[0], targetIndex)
            if clipboard.state == constants.CLIPBOARD_STATE_CUT:
                clipboard.clear()
    
    def __invalidateFilterModel(self): # Otherwise a segm. fault calling mapToSource can occur
        """ Invalidates the filter model. """
        
        try:
            self._widget.model().invalidate()
        except AttributeError:
            return
            
    @staticmethod
    def _mapIndexToSource(index):
        """ Maps the index to the coordinates of the source model. """
        
        try:
            index = index.model().mapToSource(index)
        except AttributeError:
            index = index 
        return index
                    
    def deleteAction(self, parentIndex=None):
        """ Deletes the currently selected items. """
        
        selectedIndexes = self._determineSelectedIndexes()
        count = len(selectedIndexes)
        if count > 0:
            if count > 1:
                text = "Do you really want to remove the selected items?"
            else:
                item = selectedIndexes[0].model().nodeFromIndex(selectedIndexes[0])
                text = "Do you really want to remove '%s'?" % item.path

            result = self._askDeletionOptions(text)
            if result != QtGui.QMessageBox.Cancel:
                ignoreStorageLocation = False
                if result == QtGui.QMessageBox.RejectRole:
                    ignoreStorageLocation = True
                    
                if parentIndex is None:
                    parentIndex = self._sourceRepositoryModel.parent(selectedIndexes[0])
                
                self._sourceRepositoryModel.activeIndex = parentIndex
                self._sourceRepositoryModel.lock([parentIndex])
                def cb():
                    self._sourceRepositoryModel.activeIndex = parentIndex
                    self._sourceRepositoryModel.unlock(parentIndex)
                self._selectionModel.clear()
                self._performWithProgressDialog("Delete", "Deleting items...", cb,
                                                self._sourceRepositoryModel.delete, selectedIndexes, ignoreStorageLocation)
    def _askDeletionOptions(self, text):
        """ Asks the user for deletion options. """
        
        questionDialog = QtGui.QMessageBox(self._mainWindow)
        questionDialog.setWindowTitle("Delete")
        questionDialog.setIcon(QtGui.QMessageBox.Question)
        questionDialog.setText(text)
        questionDialog.setModal(True)
        
        questionDialog.addButton(QtGui.QMessageBox.Cancel)
        if self._sourceRepositoryModel.isManagedRepository:
            questionDialog.addButton("&Complete", QtGui.QMessageBox.YesRole)
            questionDialog.addButton("&Ignore Storage Location", QtGui.QMessageBox.NoRole)
        else:
            questionDialog.addButton(QtGui.QMessageBox.Yes)
        questionDialog.setDefaultButton(QtGui.QMessageBox.Cancel)
        return questionDialog.exec_()

    def renameAction(self, index, newName):
        """ Starts the renaming of the currently selected item. """

        sourceIndex = self._mapIndexToSource(index)
        targetIndex = self._sourceRepositoryModel.parent(sourceIndex)
        sourceIndex = QtCore.QModelIndex(sourceIndex)
        sourceItem = self._sourceRepositoryModel.nodeFromIndex(sourceIndex)
        if sys.platform == "win32" and not newName.endswith(".lnk") and sourceItem.uri.startswith("file:///") and sourceItem.isLink:
            newName += ".lnk"
        self._sourceRepositoryModel.activeIndex = targetIndex
        self._sourceRepositoryModel.lock([targetIndex])
        cb = lambda: self._sourceRepositoryModel.unlock(targetIndex)
        self._performWithProgressDialog("Rename", "Renaming item...", cb,
                                        self._sourceRepositoryModel.move, [sourceIndex], targetIndex, newName)
        
    def createCollection(self):
        """ Creates a new collection under the current collection. """
        
        self._showCreationWizard(CreationWizard.COLLECTION_STATE)
    
    def createLeaf(self):
        """ Creates a new leaf under the current collection. """
        
        self._showCreationWizard(CreationWizard.LEAF_STATE)

    def createLink(self):
        """ Creates a new link under the current collection. """
        
        self._showCreationWizard(CreationWizard.LINK_STATE, self._determineSelectedIndexes())
    
    def createArchive(self):
        """ Starts the wizard for archive creation. """
        
        self._showCreationWizard(CreationWizard.ARCHIVE_STATE, self._determineSelectedIndexes())
    
    def importAction(self):
        """ Imports items under the selected collection. """

        self._showCreationWizard(CreationWizard.IMPORT_STATE, self._determineSelectedIndexes())
    
    def exportAction(self):
        """ Exports items to a specific repository. """
        
        self._showCreationWizard(CreationWizard.EXPORT_STATE, self._determineSelectedIndexes())

    def _showCreationWizard(self, state, preSelectedSourceIndexes=None):
        """ Display the creation wizard with given state. """
        
        self._creationWizard = CreationWizard(self._sourceRepositoryModel, self._targetRepositoryModel, 
                                              self._mainWindow, preSelectedSourceIndexes)
        self._selectionModel.clear()
        self._creationWizard.start(state)

    def propertiesAction(self):
        """ Opens the property dialog showing property details. """
        
        index = self._mapIndexToSource(self._selectionModel.currentIndex())
        propertyModel = PropertiesModel(self._sourceRepositoryModel)
        propertyModel.itemIndex = index
        dialog = PropertiesDialog(propertyModel, self._mainWindow)
        dialog.exec_()

    def openAction(self):
        """ Opens the selected item in a specific editor. """
        
        selectedIndexes = self._determineSelectedIndexes()
        if len(selectedIndexes) > 0:
            item = self._sourceRepositoryModel.nodeFromIndex(selectedIndexes[0])
            if item.isLink:
                buddyItem = item.linkTarget
            else:
                buddyItem = item
            
            if not buddyItem is None:
                index = self._sourceRepositoryModel.indexFromPath(buddyItem.path)
                if buddyItem.isLeaf:
                    self._performWithProgressDialog("Open", "Opening item '%s'..." % item.path, None,
                                                    self._sourceRepositoryModel.performOpen, index)
                else:
                    self._sourceRepositoryModel.activeIndex = index
                
    def printAction(self):
        """ Prints the selected item. """
        
        selectedIndexes = self._determineSelectedIndexes()
        if len(selectedIndexes) > 0:
            item = self._sourceRepositoryModel.nodeFromIndex(selectedIndexes[0])
            if item.isLink:
                buddyItem = item.linkTarget
            else:
                buddyItem = item
            if not buddyItem is None:
                if buddyItem.isLeaf:
                    index = self._sourceRepositoryModel.indexFromPath(buddyItem.path)
                    self._performWithProgressDialog("Print", "Printing item '%s'..." % item.path, None,
                                                    self._sourceRepositoryModel.performPrint, index)

    def selectAllAction(self):
        """ Selects all items in the current view. """

        parent = self._widget.rootIndex()
        row = self._widget.model().rowCount(parent) - 1
        column = self._widget.model().columnCount(parent) - 1
        
        selection = QtGui.QItemSelection(self._widget.model().index(0, 0, parent),
                                         self._widget.model().index(row, column, parent))
        self._selectionModel.select(selection, QtGui.QItemSelectionModel.Select)

    def reverseSelectionAction(self):
        """ Inverts the current selection. """

        parent = self._widget.rootIndex()
        row = self._widget.model().rowCount(parent) - 1
        column = self._widget.model().columnCount(parent) - 1
        allSelection = QtGui.QItemSelection(self._widget.model().index(0, 0, parent),
                                            self._widget.model().index(row, column, parent))
        
        currentSelection = self._selectionModel.selection()
        currentSelection.merge(allSelection, QtGui.QItemSelectionModel.Toggle)
        self._selectionModel.clear()
        self._selectionModel.select(currentSelection, QtGui.QItemSelectionModel.Select)

    def searchAction(self):
        """ Shows the search dialog. """

        if self._searchDialog is None:
            self._searchDialog = SearchDialog(self._sourceRepositoryModel, self._mainWindow, self)
        self._searchDialog.show()

    def commitArchive(self):
        """ Commits the selected archives. """
        
        selectedIndexes = self._determineSelectedIndexes()
        if len(selectedIndexes) > 0:
            parentIndex = self._sourceRepositoryModel.parent(selectedIndexes[0])
            self._sourceRepositoryModel.activeIndex = parentIndex
            self._sourceRepositoryModel.lock([parentIndex])
            def cb():
                self._sourceRepositoryModel.activeIndex = parentIndex
                self._sourceRepositoryModel.unlock(parentIndex)
            self._performWithProgressDialog("Commit Archives", "Committing archives...", cb,
                                            self._sourceRepositoryModel.commitArchive, selectedIndexes)    

    def clear(self):
        """ Cleans up the everything. """
        
        if not self._searchDialog is None and self._searchDialog.isVisible():
            self._searchDialog.close()
        self._searchDialog = None

    def _performWithProgressDialog(self, windowTitle, labelText, callbackFunction, function, *args, **kwargs): # W0142
        """ Performs the given action using the progress dialog. """

        self._progressDialog = ProgressDialog(windowTitle, labelText, parent=self._mainWindow)
        self._progressDialog._cb = callbackFunction
        self._progressDialog.start(function, *args, **kwargs)

    def createContextMenu(self, disableActions, prependActions=None):
        """ 
        Creates a default context menu of enabled actions and returns it.

        @param disableActions: List of action constants which should be ignored,
        @type disableActions: C{list} of C{unicode}
        @param prependActions: List of actions before the default actions.
        @type prependActions: C{list} of C{QAction<QtGui.QAction>} 
        
        @return: The created context menu.
        @rtype: L{QMenu<QtGui.QMenu>}
        """

        menu = self._createDefaultContextMenu(disableActions, prependActions)
        
        for action in menu.actions():
            if action.isVisible():
                menu.setDefaultAction(action)
                break
        return menu

    def _createDefaultContextMenu(self, disableActions, prependActions):
        """ Creates the default context menu. """
        
        menu = QtGui.QMenu(self._mainWindow)
        if not prependActions is None:
            menu.addActions(prependActions)
            menu.addSeparator()
        if not ac.OPEN_ACTION in disableActions:
            menu.addAction(self._mainWindow.openAction)
            menu.addSeparator()
        if not ac.USE_SCRIPT_ACTION in disableActions:
            menu.addMenu(self._scriptController.useScriptMenu)
            menu.addSeparator()
        if not (ac.CREATE_ARCHIVE_ACTION in disableActions \
                and ac.CREATE_COLLECTION_ACTION in disableActions \
                and ac.CREATE_LEAF_ACTION in disableActions \
                and ac.CREATE_LINK_ACTION in disableActions):
            menu.addMenu(self._mainWindow.newMenu)
            menu.addSeparator()
        if not ac.PRINT_ACTION in disableActions:
            menu.addAction(self._mainWindow.printAction)
            menu.addSeparator()
        if not ac.IMPORT_ACTION in disableActions:
            menu.addAction(self._mainWindow.importAction)
        if not ac.EXPORT_ACTION in disableActions:
            menu.addAction(self._mainWindow.exportAction)
            menu.addSeparator()
        if not ac.COMMIT_ARCHIVE_ACTION in disableActions:
            menu.addAction(self._mainWindow.commitArchiveAction)
            menu.addSeparator()
        if not ac.SEARCH_ACTION in disableActions:
            menu.addAction(self._mainWindow.searchAction)
            menu.addSeparator()
        for action in self._mainWindow.editMenu.actions():
            if not unicode(action.objectName()) in disableActions:
                menu.addAction(action)
        return menu
    
    def setItemActionEnabledState(self):
        """ Enables items for the current selection. """
        
        if self._sourceRepositoryModel.initialized:
            selectedIndexes = self._determineSelectedIndexes()
            
            items = [self._sourceRepositoryModel.nodeFromIndex(index) for index in selectedIndexes]
            availableActionConstants = self._itemActionChecker.determineAvailableItemActions(items)
    
            for actionName in self._itemActionChecker.ALL_ITEM_ACTIONS:
                try:
                    action = getattr(self._mainWindow, actionName)
                    action.setEnabled(actionName in availableActionConstants \
                                      and not actionName in self._disabledActions)
                except AttributeError:
                    self._logger.debug("Action '%s' can not be found." % actionName)
        
    @property
    def _selectionModel(self):
        """ Returns the current selection model. """
        
        if not self._widget is None:
            return self._widget.selectionModel()
                
class _ItemActionChecker(object):
    """ Checks availability of actions for a specific set of items. """
    
    _DEFAULT_ITEM_ACTIONS = [ac.SEARCH_ACTION, ac.CREATE_LEAF_ACTION, ac.CREATE_LINK_ACTION, ac.CREATE_COLLECTION_ACTION,
                             ac.CREATE_ARCHIVE_ACTION, ac.IMPORT_ACTION, ac.EXPORT_ACTION, ac.PASTE_ACTION, 
                             ac.SELECT_ALL_ACTION, ac.REVERSE_SELECTION]
    _MULTI_ITEM_ACTIONS = _DEFAULT_ITEM_ACTIONS + [ac.COPY_ACTION, ac.CUT_ACTION, ac.DELETE_ACTION, ac.COMMIT_ARCHIVE_ACTION, ac.USE_SCRIPT_ACTION]
    _SINGLE_ITEM_ACTIONS = _MULTI_ITEM_ACTIONS + \
                           [ac.RENAME_ACTION, ac.COPY_PROPERTIES_ACTION, ac.EDIT_PROPERTIES_ACTION, ac.PRINT_ACTION, 
                            ac.OPEN_ACTION]
    ALL_ITEM_ACTIONS = _SINGLE_ITEM_ACTIONS

    _ACTION_CHECK_MAP = {ac.CREATE_ARCHIVE_ACTION: lambda item: item.capabilities.canArchive,
                         ac.COPY_ACTION: lambda item: item.capabilities.canCopy,
                         ac.COPY_PROPERTIES_ACTION: lambda item: item.capabilities.canRetrieveProperties,
                         ac.CUT_ACTION: lambda item: item.capabilities.canMove,
                         ac.DELETE_ACTION: lambda item: item.capabilities.canDelete,
                         ac.OPEN_ACTION: lambda item: not item.isLeaf or item.capabilities.canRetrieveData,
                         ac.PRINT_ACTION: lambda item: item.capabilities.canRetrieveData,
                         ac.SEARCH_ACTION: lambda item: item.capabilities.canSearch,
                         ac.RENAME_ACTION: lambda item: item.capabilities.canMove,
                         ac.COMMIT_ARCHIVE_ACTION: lambda item: item.state in [ITEM_STATE_ARCHIVED, ITEM_STATE_ARCHIVED_READONLY]} 
    
    _ITEMTYPE_INVALID_ACTION_MAP = {(True, False): list(), # leaf
                                    (False, False): list(), # link
                                    (False, True) : [ac.PRINT_ACTION]} # collection
    
    def __init__(self, sourceRepositoryModel, targetRepositoryModel, scriptController):
        """ Constructor. """
        
        self._sourceRepositoryModel = sourceRepositoryModel
        self._targetRepositoryModel = targetRepositoryModel
        self._scriptController = scriptController
        
    def determineAvailableItemActions(self, items):
        """ 
        Creates a default context menu of enabled actions and returns it.

        @param items: List of items.
        @type items: C{list} of L{ItemBase<datafinder.core.item.base.ItemBase>} 
        
        @return: List of available action identified by the defined string constants.
        @rtype: C{list} of C{unicode}
        """
        
        availableItemActions = self._DEFAULT_ITEM_ACTIONS[:]
        if not items is None:
            numberOfItems = len(items)
            if numberOfItems == 1:
                availableItemActions = self._SINGLE_ITEM_ACTIONS[:]
            elif numberOfItems > 1:
                availableItemActions = self._MULTI_ITEM_ACTIONS[:]
            for item in items:
                self._determineAvailableItemActions(item, availableItemActions)

            for function in [self._handleCreationActions, self._handleImportActions,
                             self._handlePasteAction, self._handleSearchAction, self._handleUseScriptAction]:
                function(availableItemActions, items)
        return availableItemActions

    def _determineAvailableItemActions(self, item, availableItemActions):
        """ Determines the available actions for the given item. """
        
        for action in self._ITEMTYPE_INVALID_ACTION_MAP[(item.isLeaf, item.isCollection)]:
            if action in availableItemActions:
                availableItemActions.remove(action)

        removeActions = list()
        for action in availableItemActions:
            try:
                if not self._ACTION_CHECK_MAP[action](item):
                    removeActions.append(action)
            except KeyError:
                continue
        
        for action in removeActions:
            availableItemActions.remove(action)

    def _handleImportActions(self, availableActionConstants, _):
        """ Restricts availability of import/export action. """
        
        if self._sourceRepositoryModel.isManagedRepository:
            if ac.IMPORT_ACTION in availableActionConstants:
                availableActionConstants.remove(ac.IMPORT_ACTION)
            if not self._targetRepositoryModel.initialized and ac.EXPORT_ACTION in availableActionConstants:
                availableActionConstants.remove(ac.EXPORT_ACTION)
        else:
            if ac.EXPORT_ACTION in availableActionConstants:
                availableActionConstants.remove(ac.EXPORT_ACTION)
                if not self._targetRepositoryModel.initialized and ac.IMPORT_ACTION in availableActionConstants:
                    availableActionConstants.remove(ac.IMPORT_ACTION)

    def _handlePasteAction(self, availableActionConstants, items):
        """ Restricts availability of the paste action. """
        
        if self._sourceRepositoryModel.clipboard.state == constants.CLIPBOARD_STATE_EMPTY \
           or len(items) != 1 and self._sourceRepositoryModel.clipboard.state == constants.CLIPBOARD_STATE_COPY_PROPERTIES \
           or (len(items) == 1 and self._sourceRepositoryModel.clipboard.state == constants.CLIPBOARD_STATE_COPY_PROPERTIES \
              and not items[0].capabilities.canStoreProperties):
            if ac.PASTE_ACTION in availableActionConstants:
                availableActionConstants.remove(ac.PASTE_ACTION)
    
    def _handleSearchAction(self, availableActionConstants, _):
        """ Restricts availability of the search action. """
        
        if not self._sourceRepositoryModel.hasMetadataSearchSupport:
            if ac.SEARCH_ACTION in availableActionConstants:
                availableActionConstants.remove(ac.SEARCH_ACTION)
                
    def _handleCreationActions(self, availableActionConstants, _):
        """ Restricts availability of the create actions. """
        
        if not self._sourceRepositoryModel.nodeFromIndex(self._sourceRepositoryModel.activeIndex).capabilities.canAddChildren:
            for action in [ac.CREATE_COLLECTION_ACTION, ac.CREATE_LEAF_ACTION, ac.CREATE_LINK_ACTION]:
                if action in availableActionConstants:
                    availableActionConstants.remove(action)
    
    def _handleUseScriptAction(self, availableActionConstants, items):
        """ Restricts availability of the use script action. """
        
        scriptsAvailable = False
        if len(items) > 0:
            dataTypeNames = list()
            dataFormatNames = list()
            for item in items:
                if not item.dataFormat is None:
                    dataFormatNames.append(item.dataFormat.name)
                if not item.dataType is None:
                    dataTypeNames.append(item.dataType.name)
            context = (self._sourceRepositoryModel.repository, items)
            scriptsAvailable = self._scriptController.scriptsAvailable(dataFormatNames, dataTypeNames, context)

        if not scriptsAvailable and ac.USE_SCRIPT_ACTION in availableActionConstants:
            availableActionConstants.remove(ac.USE_SCRIPT_ACTION)
            self._scriptController.clearUseScriptMenu()
