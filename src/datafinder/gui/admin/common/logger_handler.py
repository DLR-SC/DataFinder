#
# Created: 24.01.2008 Tobias Schlauch
# Changed: $Id: logger_handler.py 3807 2009-02-24 09:37:04Z mohr_se $
#
# Version: $Revision: 3807 $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder/
#


""""
Module provides a logging handler for the DataFinder GUIs.
"""


import logging
import Queue

from datafinder.gui.admin.common import utils


__version__ = "$LastChangedRevision: 3807 $"


_guiLogFormat = "%(asctime)s: %(levelname)s: %(message)s"
_guiDateFormat = "%H:%M:%S"

_levelHtmlDirective = {logging.INFO: "<font color='black'>%s</font>",
                       logging.WARNING: "<font color='orange'>%s</font>",
                       logging.ERROR: "<font color='red'>%s</font>"}


class GuiLoggerHandler(logging.Handler):
    """
    Handler class used to display logging messages in a widget.
    The logging widget used for output has only to implement the method C{append}
    that takes a C{unicode} as input, the method C{scrollToBottom} and the method C{clear}.
    """

    def __init__(self, logWidget, level=logging.INFO):
        """
        Constuctor.

        @param logWidget: A qt widget with an C{append} interface.
        @type logWidget: L{QWidget<qt.QWidget>}
        @param level: Level constant. @see: L{logging<logging>} module.
        """

        logging.Handler.__init__(self, level)

        formatter = logging.Formatter(_guiLogFormat, _guiDateFormat)
        self.setFormatter(formatter)

        self.__callbackHandler = utils.CallbackEventHandler()
        self.__logWidget = logWidget
        self.__logMessageQueue = Queue.Queue()


    def emit(self, record):
        """
        @see: L{emit<logging.Handler.emit>}
        """

        message = self.format(record)

        if self.level <= record.levelno:
            if record.levelno in _levelHtmlDirective:
                message = _levelHtmlDirective[record.levelno] % message
            self.__callbackHandler.callFunctionInQtThread(self.__logWidget.append, False, message)
            self.__callbackHandler.callFunctionInQtThread(self.__logWidget.scrollToBottom, False)


def installGuiLoggingHandler(logger, logWidget, level=logging.INFO):
    """ Adds and configures a GuiLoggerHandler to the given logger. """

    logWidget.clear()
    guiLoggerHandler = GuiLoggerHandler(logWidget, level)
    logger.addHandler(guiLoggerHandler)
