# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#
#met:
#
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


""""
Module provides a logging handler for the DataFinder GUIs.
"""


import logging
import Queue

from datafinder.gui.admin.common import utils


__version__ = "$Revision-Id:$" 


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
