# pylint: disable-msg=R0913 
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
This module controls the tool bar view.
"""



from PyQt4 import QtCore, QtGui

from datafinder.gui.user.common import util
from datafinder.gui.user.common.delegate import AbstractDelegate
from datafinder.gui.user.common.controller import AbstractController


__version__ = "$LastChangedRevision: 4475 $"


class ToolbarController(AbstractController):
    """ Controls the tool bar view including navigation in item history. """

    def __init__(self, forwardAction, backwardAction, parentDirectoryAction, 
                 refreshAction, toolbarAction, widget, mainWindow, parentController): # R0913
        """
        Constructor.
        """

        AbstractController.__init__(self, widget, mainWindow, parentController=parentController)
        self._toolbarAction = toolbarAction
        
        self.forwardAction = forwardAction
        self.forwardMenu = QtGui.QMenu(widget)
        self.forwardAction.setData(QtCore.QVariant(1))
        self.forwardAction.setMenu(self.forwardMenu)
        
        self.backwardAction = backwardAction
        self.backwardMenu = QtGui.QMenu(widget)
        self.backwardAction.setData(QtCore.QVariant(-1))
        self.backwardAction.setMenu(self.backwardMenu)
        
        self.parentDirectoryAction = parentDirectoryAction
        self.refreshAction = refreshAction
        self._delegate = _ToolbarDelegate(self)

        self.setActivated(False)
        
    def setActivated(self, activated):
        """ 
        Activates or deactivates of the tool bar.
        """
        
        self.widget.setEnabled(activated)
        if activated:
            self.forwardAction.setEnabled(not activated)
            self.backwardAction.setEnabled(not activated)
            self.parentDirectoryAction.setEnabled(not activated)
            self.refreshAction.setEnabled(activated)
        else:
            self.forwardAction.setEnabled(activated)
            self.backwardAction.setEnabled(activated)
            self.parentDirectoryAction.setEnabled(activated)
            self.refreshAction.setEnabled(activated)

    def createHistoryMenu(self, pathlist, menu, iterator):
        """
        Create a menu from the given list with L{QtCore.QModelIndex} objects.

        @param pathlist: List of history paths objects.
        @type pathlist: C{list}
        @param menu: Menu to which the given path list will added to.
        @type menu: C{QtGui.QMenu}
        @param iterator: The iterator that specifies if the menu will move relative forward or backward.
        @type iterator: C{int}
        """

        menu.clear()
        for steps, path in enumerate(pathlist):
            action = QtGui.QAction(path, menu)
            action.setData(QtCore.QVariant((steps + 1) * iterator))
            QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), self._createJumpToPathActionSlot(action))
            menu.addAction(action)

        if len(pathlist):
            menu.setDefaultAction(menu.actions()[0])

    def _createJumpToPathActionSlot(self, action):
        """ Creates a slot which directly jumps to the associated path in the history. """
        
        def _jumpToPathActionSlot():
            steps, success = action.data().toInt()
            if success:
                self.model.relativeHistoryIndex = steps
        return _jumpToPathActionSlot


class _ToolbarDelegate(AbstractDelegate):
    """
    This delegate is responsible for user interactions with the L{ToolbarView}.
    """

    def __init__(self, controller):
        """
        Constructor.
        """

        AbstractDelegate.__init__(self, controller)
        self._thread = None
        self._searchDialog = None

    @util.immediateConnectionDecorator("model", "updateSignal")
    def _modelUpdatedSlot(self, index):
        """
        Slot is called if the model has changed.
        """

        backwardList, forwardList = self._controller.model.history

        self._controller.createHistoryMenu(forwardList, self._controller.forwardMenu, 1)
        self._controller.createHistoryMenu(backwardList, self._controller.backwardMenu, -1)
       
        self._controller.forwardAction.setEnabled(len(forwardList) > 0)
        self._controller.backwardAction.setEnabled(len(backwardList) > 1)

        self._controller.parentDirectoryAction.setEnabled(index.isValid())
        
    @util.immediateConnectionDecorator("backwardAction", "triggered()")
    def _historyBackwardClickedSlot(self):
        """
        Slot is called if an action was triggered in one of the history menus.

        @param action: The action that was pressed in the history menu.
        @type action: C{QtGui.QMenu}
        """

        steps, success = self._controller.backwardAction.data().toInt()
        if success:
            self._controller.model.relativeHistoryIndex = steps

    @util.immediateConnectionDecorator("forwardAction", "triggered()")
    def _historyForwardClickedSlot(self):
        """
        Slot is called if an action was triggered in one of the history menus.

        @param action: The action that was pressed in the history menu.
        @type action: C{QtGui.QMenu}
        """

        steps, success = self._controller.forwardAction.data().toInt()
        if success:
            self._controller.model.relativeHistoryIndex = steps

    @util.immediateConnectionDecorator("_toolbarAction", "triggered(bool)")
    def _showToolbar(self, showIt):
        """ Shows / hides the tool bar. """

        self._controller.setVisible(showIt)

    @util.immediateConnectionDecorator("parentDirectoryAction", "triggered()")
    def _parentDirectoryActionTriggeredSlot(self):
        """
        Change the path to the parent directory of the path.
        """

        self._controller.model.activeIndex = self._controller.model.activeIndex.parent()

    @util.immediateConnectionDecorator("refreshAction", "triggered()")
    def _refreshActionTriggeredSlot(self):
        """ Refresh the View with the current model data. """
        
        self._controller.model.refresh(self._controller.model.activeIndex)
