#
# Created: 03.03.2008 lege_ma <malte.legenhausen@dlr.de>
# Changed: $Id: delegate.py 4475 2010-02-25 17:02:20Z schlauch $
#
# Copyright (C) 2003-2008 DLR/SISTEC, Germany
#
# All rights reserved
#
# http://www.dlr.de/datafinder/
#


"""
Base class for all delegates of the main window.
"""


from datafinder.gui.user.common import util


__version__ = "$LastChangedRevision: 4475 $"


class AbstractDelegate(object):
    """ Base class for all delegates of the main window. """

    def __init__(self, controller, scan=True):
        """
        Constructor.

        @param controller: Controller that is associated with this delegate.
        @type controller: L{AbstractController<datafinder.gui.user.common.controller.AbstractController>}
        """

        self._controller = controller
        self._mainWindow = controller.mainWindow
        self.__connectionDecorator = util.QtConnectionDelegate()
        if scan:
            self.scan()

    @util.immediateConnectionDecorator("widget", "modelUpdateSignal")
    def _establishUnresolvedConnections(self):
        """ Establishes connection which have not been resolved on initialization. """

        self.__connectionDecorator.establishUnresolvedConnections()

    @util.immediateConnectionDecorator("widget", "focusSignal")
    def _establishDeferredConnections(self, establish):
        """ Establishes / Removes connections when the corresponding widget has got/lost the focus. """

        if establish:
            self.__connectionDecorator.establishDeferredConnections()
        else:
            self.__connectionDecorator.removeDeferredConnections()

    def scan(self):
        """ Methods to scan the instance for slots. """

        self.__connectionDecorator.scan(self, [self._controller, self._controller.mainWindow, self])
