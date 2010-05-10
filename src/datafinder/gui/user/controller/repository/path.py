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
Controls the path editor view.
"""


from datafinder.gui.user.common.delegate import AbstractDelegate
from datafinder.gui.user.common import util
from datafinder.gui.user.common.controller import AbstractController


__version__ = "$LastChangedRevision: 4475 $"


class PathController(AbstractController):
    """ Controls the path editor view. """

    def __init__(self, pathLineEdit, mainWindow, parentController):
        """
        Constructor.
        """

        AbstractController.__init__(self, pathLineEdit, mainWindow, parentController=parentController)

        self._delegates = [PathDelegate(self)]


class PathDelegate(AbstractDelegate):
    """
    This delegates manages all interactions with the path line edit.
    """

    def __init__(self, controller):
        """ Constructor. """

        AbstractDelegate.__init__(self, controller)

    @util.immediateConnectionDecorator("model", "updateSignal")
    def _updateSignalSlot(self):
        """ Slot is called when the model has changed. """

        path = self._controller.model.activePath
        self._controller.setText(path or "/")

    @util.immediateConnectionDecorator("widget", "returnPressed()")
    def _returnPressedSlot(self):
        """ Slot called if a path was entered. """
        
        path = unicode(self._controller.text())
        self._controller.model.activePath = path
