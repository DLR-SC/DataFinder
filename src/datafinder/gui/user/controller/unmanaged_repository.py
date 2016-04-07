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
 Controller for the unmanaged data repository.
"""

import os

from datafinder.gui.user.common.controller import AbstractController
from datafinder.gui.user.controller.item_actions import ItemActionController
from datafinder.gui.user.controller.repository.path import PathController
from datafinder.gui.user.controller.repository.toolbar import ToolbarController
from datafinder.gui.user.controller.repository.tree import TreeController
from datafinder.gui.user.controller.repository.collection import StackedCollectionsController
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter
from datafinder.gui.user.models.repository.repository import RepositoryModel


__version__ = "$Revision-Id:$" 


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
        self.model.activePath = os.path.expanduser("~")
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
