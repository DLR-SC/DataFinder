#
# Created: 13.07.2007 lege_ma <malte.legenhausen@dlr.de>
# Changed:
#
# Copyright (C) 2003-2007 DLR/SISTEC, Germany
#
# All rights reserved
#
# http://www.dlr.de/datafinder
#


"""
Controller for shared managed data repository.
"""


import logging

from PyQt4 import QtGui, QtCore

from datafinder.core.error import ConfigurationError, ItemError
from datafinder.gui.user.constants import LOGGER_ROOT
from datafinder.gui.user.common.controller import AbstractController
from datafinder.gui.user.common.delegate import AbstractDelegate
from datafinder.gui.user.common import util
from datafinder.gui.user.controller.item_actions import ItemActionController
from datafinder.gui.user.controller.repository.path import PathController
from datafinder.gui.user.controller.repository.tree import TreeController
from datafinder.gui.user.controller.repository.collection import StackedCollectionsController
from datafinder.gui.user.controller.repository.properties import PropertiesController
from datafinder.gui.user.controller.repository.toolbar import ToolbarController
from datafinder.gui.user.dialogs.connect_dialog import ConnectDialogView
from datafinder.gui.user.dialogs.datastores_dialog import DatastoresDialog
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter
from datafinder.gui.user.models.properties import PropertiesModel
from datafinder.gui.user.models.repository.repository import RepositoryModel


__version__ = "$LastChangedRevision: 4615 $"


class ManagedRepositoryController(AbstractController):
    """
    Controller of the shared data repository.
    """

    def __init__(self, mainWindow, repositoryManager):
        """
        Constructor.

        @param mainWindow: The main window component of the DataFinder User Client.
        @type mainWindow: L{MainWindow<datafinder.gui.user.application.MainWindow>}
        @param repositoryManager: Management component of data repositories.
        @type repositoryManager: L{RepositoryManager<datafinder.core.repository_manager.RepositoryManager>}
        """
        
        AbstractController.__init__(self, mainWindow.serverDockWidget, mainWindow)
        
        self._toolbarController = ToolbarController(mainWindow.serverForwardAction,
                                                    mainWindow.serverBackwardAction,
                                                    mainWindow.serverParentCollectionAction,
                                                    mainWindow.serverRefreshAction,
                                                    mainWindow.serverToolbarAction,
                                                    mainWindow.serverToolBar,
                                                    mainWindow,
                                                    self)
        self._pathController = PathController(mainWindow.serverPathLineEdit, mainWindow, self)
        self._treeController = TreeController(mainWindow.serverTreeView, mainWindow, self)
        self._propertiesController = PropertiesController(mainWindow, self)
        self.collectionController = StackedCollectionsController(mainWindow.serverStackedWidget,
                                                                 mainWindow.serverTableView,
                                                                 mainWindow.serverListView,
                                                                 mainWindow.serverViewsListAction,
                                                                 mainWindow.serverViewsTableAction,
                                                                 mainWindow.serverViewsIconsAction,
                                                                 mainWindow,
                                                                 self)
        self.setEnabled(False)
        self.model = RepositoryModel(repositoryManager.preferences)
        self._itemActionController = None
        self._unmanagedRepositoryController = None
        self._scriptController = None
        
        self._delegate = _ManagedRepositoryDelegate(self, repositoryManager)

    def _layoutChanged(self):
        """ Correctly focuses the collection widget when layout changed. """
        
        self.focus()
        QtCore.QObject.disconnect(self.model, QtCore.SIGNAL("layoutChanged()"), self._layoutChanged)
        
    def load(self, unmanagedRepositoryController, scriptController):
        """
        Initializes the managed repository controller.

        @param unmanagedRepositoryModel: The unmanaged repository controller.
        @type unmanagedRepositoryModel: L{UnmanagedRepositoryController<datafinder.gui.user.controller.unmanaged_repository.UnmanagedRepositoryController>}
        @param scriptController: The script controller component used to get access to registered script extensions.
        @type scriptController: L{ScriptController<datafinder.gui.user.controller.scripts.ScriptController>}
        """

        self._unmanagedRepositoryController = unmanagedRepositoryController
        self._delegate._scriptController = scriptController
        self._itemActionController = ItemActionController(self.mainWindow, self.model, 
                                                          unmanagedRepositoryController.model, scriptController)
        
        self._toolbarController.model = self.model
        self._pathController.model = self.model
        self._treeController.model = LeafFilter(self.model)
        self.collectionController.model = self.model
        self._propertiesController.model = PropertiesModel(self.model)

    def focus(self):
        """ Focuses the managed repository. """

        self.collectionController.focus()
        
    def setEnabled(self, flag):
        """ 
        Sets the enabled state of the managed repositories view.
        
        @param flag: Indicating enabled state.
        @type flag: C{bool}
        """
        
        self._toolbarController.setEnabled(flag)
        self._pathController.setEnabled(flag)
        self._treeController.setEnabled(flag)
        self.collectionController.setEnabled(flag)
        self._propertiesController.setEnabled(flag)
        self.mainWindow.connectAction.setEnabled(not flag)
        self.mainWindow.selectDatastoresAction.setEnabled(flag)
        
    def setConnectionState(self, success):
        """ Sets the connection state. """
        
        self.mainWindow.disconnectAction.setVisible(success)
        self.mainWindow.connectAction.setVisible(not success)
        if not success:
            self._pathController.clear()
            self.itemActionController.clear()
            self._unmanagedRepositoryController.focus()
        else:
            QtCore.QObject.connect(self.model, QtCore.SIGNAL("layoutChanged()"), self._layoutChanged)
        self._toolbarController.setActivated(success)
        self.setEnabled(success)
        
    @property
    def itemActionController(self):
        """
        @return: ItemActionControler instance of this repository.
        @rtype: L{ItemActionController<datafinder.gui.user.controller.item_actions.ItemActionController>}
        """
        
        return self._itemActionController


class _ManagedRepositoryDelegate(AbstractDelegate):
    """
    This delegate handles all global user interactions with the server side.
    """

    _logger = logging.getLogger(LOGGER_ROOT)
    _workerThread = None
    
    def __init__(self, controller, repositoryManager):
        """
        Constructor.

        @param controller: The controller that is associated with this delegate.
        @type controller: L{AbstractController<datafinder.gui.user.common.controller.AbstractController>}
        """

        AbstractDelegate.__init__(self, controller)
        
        self._mainWindow.connectAction.setEnabled(True)
        self._mainWindow.disconnectAction.setEnabled(True)
        
        self._repositoryManager = repositoryManager
        self._model = self._controller.model 
        self._scriptController = None

    @util.immediateConnectionDecorator("disconnectAction", "triggered()")
    def _disconnectActionSlot(self):
        """
        Slot is called when the disconnection action was triggered.
        """
        
        self._controller.model.clear()
        self._scriptController.clearSharedScripts()
        self._controller.setConnectionState(False)
        
    @util.immediateConnectionDecorator("connectAction", "triggered()")
    def _connectActionSlot(self):
        """
        Shows the connect dialog for establishing a connection to a repository.
        """

        connectDialog = ConnectDialogView(self._mainWindow, self._repositoryManager.preferences)
        if connectDialog.exec_() == QtGui.QDialog.Accepted:
            self._mainWindow.connectAction.setEnabled(False)
            defaultDataStore = None
            defaultArchiveStore = None
            defaultOfflineStore = None
            connection = self._repositoryManager.preferences.getConnection(connectDialog.uri)
            if not connection is None:
                defaultDataStore = connection.defaultDataStore
                defaultArchiveStore = connection.defaultArchiveStore
                defaultOfflineStore = connection.defaultOfflineStore

            password = None
            if connectDialog.savePasswordFlag:
                password = connectDialog.password
            self._repositoryManager.preferences.addConnection(connectDialog.uri, connectDialog.username, password,
                                                              defaultDataStore, defaultArchiveStore, defaultOfflineStore) 
            try:
                self._repositoryManager.savePreferences()
            except ConfigurationError, error:
                self._logger.error("Cannot connect repository. Reason: '%s'" % error.message)
                self._mainWindow.connectAction.setEnabled(True)
            else:
                self._workerThread = util.startNewQtThread(self._doConnect, self._connectCallback, 
                                                           connectDialog.uri, connectDialog.username, connectDialog.password)
                
    def _connectCallback(self):
        """ Callback for the thread establishing the repository connection. """
        
        repository = self._workerThread.result

        if not repository is None:
            self._model.load(repository)
            self._scriptController.loadSharedScripts(repository.configuration.scripts)
            self._controller.setConnectionState(True)
        else:
            self._mainWindow.connectAction.setEnabled(True)

    def _doConnect(self, uri, username, password):
        """ Performs the repository connection. """

        repository = None
        repositoryConfiguration = None
        try:
            repositoryConfiguration = self._repositoryManager.getRepositoryConfiguration(uri, username, password)
            repositoryConfiguration.load()
        except ConfigurationError, error:
            self._logger.error("Cannot load repository configuration.\nReason: '%s'" % error.message)
            if not repositoryConfiguration is None:
                repositoryConfiguration.release()
        else:
            try:
                repository = self._repositoryManager.connectRepository(repositoryConfiguration.defaultDataUris[0], repositoryConfiguration, 
                                                                       username, password)
            except ConfigurationError, error:
                self._logger.error("Cannot connect repository.\nReason: '%s'" % error.message)
            else:
                try:
                    repository.root.getChildren()
                except ItemError, error:
                    self._logger.error("Cannot retrieve children of the root item.\nReason: '%s'" % error.message)
                    repository = None
        return repository

    @util.immediateConnectionDecorator("selectDatastoresAction", "triggered()")
    def _selectDatastoresSlot(self):
        """ Shows the data store selection dialog. """

        dialog = DatastoresDialog(self._mainWindow)
        if self._model.initialized:
            dialog.load([ds.name for ds in self._model.repository.configuration.onlineDatastores],
                        [ds.name for ds in self._model.repository.configuration.archiveDatastores],
                        [ds.name for ds in self._model.repository.configuration.offlineDatastores])
            
            configurationUri = self._model.repository.configuration.repositoryConfigurationUri
            connection = self._repositoryManager.preferences.getConnection(configurationUri)
            if not connection is None:
                dialog.defaultDataStore = connection.defaultDataStore
                dialog.defaultArchiveStore = connection.defaultArchiveStore
                dialog.defaultOfflineStore = connection.defaultOfflineStore
                
            if dialog.exec_() == QtGui.QDialog.Accepted:
                self._repositoryManager.preferences.addConnection(configurationUri, connection.username, connection.password, 
                                                                  dialog.defaultDataStore, dialog.defaultArchiveStore, 
                                                                  dialog.defaultOfflineStore)
                self._repositoryManager.savePreferences()
