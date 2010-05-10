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
Controller for the unmanaged data repository.
"""


from datafinder.gui.user.common.controller import AbstractController
from datafinder.gui.user.controller.item_actions import ItemActionController
from datafinder.gui.user.controller.repository.path import PathController
from datafinder.gui.user.controller.repository.toolbar import ToolbarController
from datafinder.gui.user.controller.repository.tree import TreeController
from datafinder.gui.user.controller.repository.collection import StackedCollectionsController
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter
from datafinder.gui.user.models.repository.repository import RepositoryModel


__version__ = "$LastChangedRevision: 4578 $"


class UnmanagedRepositoryController(AbstractController):
    """
    Controller for the unmanaged data repository.
    """

    def __init__(self, mainWindow, repositoryManager):
        """
        Constructor.

        @param mainWindow: The main window component of the DataFinder User Client.
        @type mainWindow: L{MainWindow<datafinder.gui.user.application.MainWindow>}
        @param repositoryManager: Management component of data repositories.
        @type repositoryManager: L{RepositoryManager<datafinder.core.repository_manager.RepositoryManager>}
        """

        AbstractController.__init__(self, mainWindow.localDockWidget, mainWindow)
        
        self._repositoryManager = repositoryManager
        
        self._toolbarController = ToolbarController(mainWindow.localForwardAction,
                                                    mainWindow.localBackwardAction,
                                                    mainWindow.localParentDirectoryAction,
                                                    mainWindow.localRefreshAction,
                                                    mainWindow.localToolbarAction,
                                                    mainWindow.localToolBar,
                                                    mainWindow,
                                                    self)
        self._pathController = PathController(mainWindow.localPathLineEdit, mainWindow, self)
        self._treeController = TreeController(mainWindow.localTreeView, mainWindow, self)
        self.collectionController = StackedCollectionsController(mainWindow.localStackedWidget,
                                                                 mainWindow.localTableView,
                                                                 mainWindow.localListView,
                                                                 mainWindow.localViewsListAction,
                                                                 mainWindow.localViewsTableAction,
                                                                 mainWindow.localViewsIconsAction,
                                                                 mainWindow,
                                                                 self)

        self.model = RepositoryModel(repositoryManager.preferences)
        self._itemActionController = None
        
    def load(self, managedRepositoryController, scriptController):
        """
        Initializes the unmanaged repository controller.

        @param managedRepositoryController: The managed repository controller.
        @type managedRepositoryController: L{ManagedRepositoryController<datafinder.gui.user.controller.managed_repository.ManagedRepositoryController>}
        @param scriptController: The script controller component used to get access to registered script extensions.
        @type scriptController: L{ScriptController<datafinder.gui.user.controller.scripts.ScriptController>}
        """

        self._itemActionController = ItemActionController(self.mainWindow, self.model, 
                                                          managedRepositoryController.model, scriptController)
        
        configuration = self._repositoryManager.getRepositoryConfiguration()
        localRepository = self._repositoryManager.connectRepository("file:///", configuration)
        self.model.load(localRepository)
        
        self._toolbarController.model = self.model
        self._pathController.model = self.model
        self._treeController.model = LeafFilter(self.model)
        self.collectionController.model = self.model
        
        self._toolbarController.setActivated(True)
        self.model.updateSignal()
        self.collectionController.focus()

    def focus(self):
        """ Focuses the unmanaged repository. """
        
        self.collectionController.focus()
        
    @property
    def itemActionController(self):
        """
        @return: ItemActionControler instance of this repository.
        @rtype: L{ItemActionController<datafinder.gui.user.controller.item_actions.ItemActionController>}
        """
        
        return self._itemActionController
