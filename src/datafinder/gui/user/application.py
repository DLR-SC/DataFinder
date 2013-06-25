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
Application module. Indicates the start of the application and initialize the translation of
the L{datafinder.gui.user.main_window.DataFinderMainWindow}.
"""


import atexit
import logging
import sys

from PyQt4 import QtCore, QtGui

from datafinder.common import logger
from datafinder.core.repository_manager import repositoryManagerInstance
from datafinder.gui.gen.user.main_window_ui import Ui_mainWindow
from datafinder.gui.user import constants
from datafinder.gui.user.common.controller import FocusObserver
from datafinder.gui.user.controller.unmanaged_repository import UnmanagedRepositoryController
from datafinder.gui.user.controller.managed_repository import ManagedRepositoryController
from datafinder.gui.user.controller.output.facade import OutputFacadeController
from datafinder.gui.user.controller.scripts import ScriptController
from datafinder.gui.user.dialogs.about_dialog import AboutDialogView
from datafinder.gui.user.models.logger import LoggingModel, LoggingSortFilterModel, LoggerHandler
from datafinder.gui.user.models.repository.filter.search_filter import SearchFilter
from datafinder.gui.user import script_api
from datafinder.gui.user.common.widget.widget import ActionTooltipMenu
from datafinder.script_api.repository import RepositoryDescription


__version__ = "$Revision-Id:$" 


class MainWindow(Ui_mainWindow, QtGui.QMainWindow, FocusObserver):
    """
    This class defines the MainWindow of the DataFinder User Client.
    This class is a singleton and can only exists one time per datafinder instance.
    """ 

    def __init__(self, parent=None):
        """
        Constructor.

        @param parent: Parent object of the MainWindow.
        @type parent: C{QtGui.QWidget}
        """

        QtGui.QMainWindow.__init__(self, parent)
        Ui_mainWindow.__init__(self)
        FocusObserver.__init__(self)

        self.setupUi(self)

        #Set pushbuttons in the main window toolbar.
        self.copyToolButton = QtGui.QToolButton(self)
        self.copyToolButton.setDefaultAction(self.copyAction)

        self.cutToolButton = QtGui.QToolButton(self)
        self.cutToolButton.setDefaultAction(self.cutAction)

        self.pasteToolButton = QtGui.QToolButton(self)
        self.pasteToolButton.setDefaultAction(self.pasteAction)

        self.deleteToolButton = QtGui.QToolButton(self)
        self.deleteToolButton.setDefaultAction(self.deleteAction)

        for button in (self.deleteToolButton, self.pasteToolButton, self.cutToolButton, self.copyToolButton):
            button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            self.mainToolbar.addWidget(button)
        self.mainToolbar.addSeparator()
        self.mainToolbar.addAction(self.searchAction)

        #Wrapper button for the upload action.
        self.uploadToolButton = QtGui.QToolButton(self)
        self.uploadToolButton.setDefaultAction(self.importAction)

        self.localToolBar = QtGui.QToolBar(self.localDockWidgetContents)
        self._initLocalToolbar()
        
        #Local back button configuration.
        self.localBackButton = self.localToolBar.widgetForAction(self.localBackwardAction)
        self.localBackButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.localBackButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.localBackButton.setEnabled(False)

        #Local forward button configuration.
        self.localForwardButton = self.localToolBar.widgetForAction(self.localForwardAction)
        self.localForwardButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.localForwardButton.setEnabled(False)

        #Set the text besides the icon for the local tree view button.
        self.localTreeViewButton = self.localToolBar.widgetForAction(self.localTreeViewAction)
        self.localTreeViewButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        self.localViewsButton = self.localToolBar.widgetForAction(self.localViewsAction)
        self.localViewsButton.setPopupMode(QtGui.QToolButton.InstantPopup)

        self.localViewsMenu = QtGui.QMenu(self.localToolBar)
        self.localViewsMenu.addAction(self.localViewsTableAction)
        self.localViewsMenu.addAction(self.localViewsListAction)
        self.localViewsMenu.addAction(self.localViewsIconsAction)
        self.localViewsAction.setMenu(self.localViewsMenu)

        self.localViewsGroup = QtGui.QActionGroup(self.localToolBar)
        self.localViewsGroup.addAction(self.localViewsTableAction)
        self.localViewsGroup.addAction(self.localViewsListAction)
        self.localViewsGroup.addAction(self.localViewsIconsAction)
        self.localViewsTableAction.setChecked(True)

        #Begin of the server site.
        self.serverParentCollectionAction.setEnabled(False)
        self.serverRefreshAction.setEnabled(False)

        #Wrapper button for the donwload action.
        self.downloadToolButton = QtGui.QToolButton(self)
        self.downloadToolButton.setDefaultAction(self.exportAction)
        
        self.serverToolBar = QtGui.QToolBar(self.serverDockWidgetContents)
        self._initServerToolbar()
        
        #Remote back button configuration.
        self.serverBackButton = self.serverToolBar.widgetForAction(self.serverBackwardAction)
        self.serverBackButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.serverBackButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.serverBackButton.setEnabled(False)

        #Remote forward button configuration.
        self.serverForwardButton = self.serverToolBar.widgetForAction(self.serverForwardAction)
        self.serverForwardButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.serverForwardButton.setEnabled(False)

        #Set the text besides the icon for the server tree view button.
        self.serverTreeViewButton = self.serverToolBar.widgetForAction(self.serverTreeViewAction)
        self.serverTreeViewButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        #Set the text besides the icon for the server property view button.
        self.serverPropertiesViewButton = self.serverToolBar.widgetForAction(self.serverPropertiesViewAction)
        self.serverPropertiesViewButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        self.serverViewsButton = self.serverToolBar.widgetForAction(self.serverViewsAction)
        self.serverViewsButton.setPopupMode(QtGui.QToolButton.InstantPopup)

        self.serverViewsMenu = QtGui.QMenu(self.serverToolBar)
        self.serverViewsMenu.addAction(self.serverViewsTableAction)
        self.serverViewsMenu.addAction(self.serverViewsListAction)
        self.serverViewsMenu.addAction(self.serverViewsIconsAction)
        self.serverViewsAction.setMenu(self.serverViewsMenu)

        self.serverViewsGroup = QtGui.QActionGroup(self.serverToolBar)
        self.serverViewsGroup.addAction(self.serverViewsTableAction)
        self.serverViewsGroup.addAction(self.serverViewsListAction)
        self.serverViewsGroup.addAction(self.serverViewsIconsAction)
        self.serverViewsTableAction.setChecked(True)

        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.localDockWidget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.serverDockWidget)
        
        #Size ratio between the treeview and the tableview on the local site.
        self.localTreeListSplitter.setSizes([100, 250])

        #Size ratio between the treeview and the tableview on the remote site.
        self.serverTreeListSplitter.setSizes([100, 250])

        #Size ratio between the remote fileviews and the propertytableview.
        self.serverAttributeSplitter.setSizes([350, 100])

        self.useScriptAction = ActionTooltipMenu()
        self.useScriptAction.setTitle("Use &Script")
        
        self.connect(self.fixToolbarAction,
                     QtCore.SIGNAL("triggered(bool)"),
                     lambda move: self.mainToolbar.setMovable(not move))
        self.connect(self.exitAction,
                     QtCore.SIGNAL("triggered()"),
                     QtGui.qApp.exit)
        
        
        self.connect(self.aboutAction, QtCore.SIGNAL("triggered()"), self.aboutDialogSlot)

    def _initLocalToolbar(self):
        """ Initializes local tool bars. """
        
        self.localToolBar.setIconSize(QtCore.QSize(32, 24))
        self.localToolBar.addAction(self.localBackwardAction)
        self.localToolBar.addAction(self.localForwardAction)
        self.localToolBar.addAction(self.localParentDirectoryAction)
        self.localToolBar.addSeparator()
        self.localToolBar.addAction(self.localTreeViewAction)
        self.localToolBar.addAction(self.localViewsAction)
        self.localToolBar.addSeparator()
        self.localToolBar.addAction(self.localRefreshAction)
        self.localToolBar.addWidget(self.uploadToolButton)
        self.localDockWidgetContents.layout().insertWidget(0, self.localToolBar)

    def _initServerToolbar(self):
        """ Initializes server tool bars. """
        
        self.serverToolBar.setIconSize(QtCore.QSize(32, 24))
        self.serverToolBar.addAction(self.serverBackwardAction)
        self.serverToolBar.addAction(self.serverForwardAction)
        self.serverToolBar.addAction(self.serverParentCollectionAction)
        self.serverToolBar.addSeparator()
        self.serverToolBar.addAction(self.serverTreeViewAction)
        self.serverToolBar.addAction(self.serverPropertiesViewAction)
        self.serverToolBar.addAction(self.serverViewsAction)
        self.serverToolBar.addSeparator()
        self.serverToolBar.addAction(self.serverRefreshAction)
        self.serverToolBar.addWidget(self.downloadToolButton)
        self.serverDockWidgetContents.layout().insertWidget(0, self.serverToolBar)

    @property
    def serverTableSelectionModel(self):
        """ Returns the selection model. """

        return self.serverTableView.selectionModel()

    @property
    def serverTreeSelectionModel(self):
        """ Returns the selection model. """
        
        return self.serverTreeView.selectionModel()
    
    @property
    def localTableSelectionModel(self):
        """ Returns the selection model. """

        return self.localTableView.selectionModel()

    @property
    def localTreeSelectionModel(self):
        """ Returns the selection model. """
        
        return self.localTreeView.selectionModel()    

    def aboutDialogSlot(self):
        """ Shows the search dialog. """
        dialog = AboutDialogView(self)
        dialog.exec_()


class Translator(QtCore.QTranslator):
    """
    Starts the internationalisation of the Datafinder.
    """

    #Path to the languages file directory.
    LANGUAGE_RESOURCE_PATH = ":/languages/languages/"
    #Prefix of the language file.
    LANGUAGE_RESOURCE_FILE = "user"

    def __init__(self):
        """
        Constructor.
        """

        QtCore.QTranslator.__init__(self)

        locale = QtCore.QLocale.system().name()
        path = "%s_%s" % (self.LANGUAGE_RESOURCE_FILE, locale)
        self.load(path, self.LANGUAGE_RESOURCE_PATH)


class Application(QtGui.QApplication):
    """
    The DataFinder application initialize all controller of the GUI.
    """

    def __init__(self, parameter, startUrl, debug):
        """
        Constructor.

        @param parameter: Parameter of the application.
        @type parameter: C{list}
        @param startUrl: The URL used for connection.
        @type startUrl: C{unicode}
        @param debug: Activates debug messages when set to C{True}.
        @type debug: C{bool}
        """

        QtGui.QApplication.__init__(self, parameter)

        pixmap = QtGui.QPixmap(":/images/images/splash_datafinder_user.png")
        splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
        splash.show()
        self.processEvents()
        
        #Initializing of the translator.
        self.__translator = Translator()
        self.installTranslator(self.__translator)

        #Initializing of the logging mechanism.
        rootLoggerHandler = LoggerHandler(constants.LOGGER_ROOT)
        rootLoggingModel = LoggingModel(rootLoggerHandler, parent=self)
        rootLogger = logging.getLogger(constants.LOGGER_ROOT)
        if debug:
            rootLogger.setLevel(logging.DEBUG)
        rootLogger.addHandler(rootLoggerHandler)
        logger.getDefaultLogger().addHandler(rootLoggerHandler)

        scriptLoggerHandler = LoggerHandler(constants.LOGGER_SCRIPT)
        scriptLoggingModel = LoggingModel(scriptLoggerHandler, parent=self)
        scriptLogger = logging.getLogger(constants.LOGGER_SCRIPT)
        scriptLogger.setLevel(logging.DEBUG)
        scriptLogger.addHandler(scriptLoggerHandler)

        #Model initialization.
        repositoryManager = repositoryManagerInstance
        repositoryManager.load()
        if repositoryManager.preferences.getConnection(startUrl) is None:
            repositoryManager.preferences.addConnection(startUrl)

        #controller initialization.
        self.__mainWindow = MainWindow()
        self.__unmanagedRepositoryController = UnmanagedRepositoryController(self.__mainWindow, repositoryManager)
        self.__managedRepositoryController = ManagedRepositoryController(self.__mainWindow, repositoryManager)
        self.__scriptController = ScriptController(repositoryManager.scriptRegistry, 
                                                   self.__unmanagedRepositoryController.model,
                                                   self.__mainWindow)
        self.__unmanagedRepositoryController.load(self.__managedRepositoryController, self.__scriptController)
        self.__managedRepositoryController.load(self.__unmanagedRepositoryController, self.__scriptController)
        
        self.__outputView = OutputFacadeController(self.__mainWindow, 
                                                   SearchFilter(self.__managedRepositoryController.model),
                                                   self.__managedRepositoryController.itemActionController)

        self.__outputView.myRootLogView.model = LoggingSortFilterModel(rootLoggingModel)
        self.__outputView.myScriptLogView.model = LoggingSortFilterModel(scriptLoggingModel)
        
        
        # Display the GUI
        self.__mainWindow.show()
        splash.finish(self.__mainWindow)

        # initialize script API and scripts
        scriptApiContext = _ScriptApiContext()
        scriptApiContext.mainWidget = self.__mainWindow
        scriptApiContext.repositoryManager = repositoryManager
        scriptApiContext.managedRepositoryController = self.__managedRepositoryController
        scriptApiContext.unmanagedRepositoryController = self.__unmanagedRepositoryController
        scriptApiContext.scriptController = self.__scriptController
        script_api._context = scriptApiContext
        self.__scriptController.load()
        
        # Register clean up stuff
        atexit.register(repositoryManager.savePreferences)

        #Log message that everything is fine...
        rootLogger.info("DataFinder successful started.")

    @staticmethod
    def exec_():
        """ This is a workaround for those systems that 
        crash on Qt exit. It is ensured that all registered
        exit functions are executed before Qt the application exits. """
        # pylint: disable=W0212
        
        QtGui.QApplication.exec_()
        try: 
            atexit._run_exitfuncs()
        except: # pylint: disable=W0702
            pass # _run_exitfuncs already prints errors to stderr


class _ScriptApiContext(object):
    """ Holds the relevant context object the script API has to access. """
    
    def __init__(self):
        """ Constructor. """
        
        self.mainWidget = None
        self.managedRepositoryController = None
        self.unmanagedRepositoryController = None
        self.repositoryManager = None
        self.progressDialog = None
        self.scriptController = None

    def determineRepositoryController(self, repositoryDescription=None):
        """ Determines the current repository. """
        # pylint: disable=W0212
        # W0212: We need to access the _repository attribute of the
        # repository description only for internal usage.

        rm = None
        if not repositoryDescription is None:
            workingRepository = repositoryDescription._repository
        else:
            workingRepository = self.repositoryManager.workingRepository
        if self.managedRepositoryController.model.repository == workingRepository:
            rm = self.managedRepositoryController
        else:
            rm = self.unmanagedRepositoryController
        return rm
    
    def determineRepositoryModel(self, repositoryDescription=None):
        """ Determines the current repository. """
    
        return self.determineRepositoryController(repositoryDescription).model
    
    @staticmethod
    def determinesIndexes(rm, paths):    
        """ Determines the indexes from the given paths. """
        
        indexes = list()
        for path in paths:
            indexes.append(rm.indexFromPath(path))
        return indexes

    @property
    def managedRepositoryDescription(self):
        """ Returns the repository descriptor of the managed repository. """
        
        return RepositoryDescription(self.managedRepositoryController.model.repository)
        
    @property
    def unmanagedRepositoryDescription(self):
        """ Returns the repository descriptor of the unmanaged repository. """
        
        return RepositoryDescription(self.unmanagedRepositoryController.model.repository)


def main(startUrl=None, debug=False):
    """ Main function to start the user client. """
    
    application = Application(sys.argv, startUrl, debug)
    sys.exit(application.exec_())
