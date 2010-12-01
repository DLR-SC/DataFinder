# pylint: disable=R0201, W0142, W0611
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:
# All rights reserved.
#
#
# * Redistributions of source code must retain the above copyright 
#
#   notice, this list of conditions and the following disclaimer. 
#
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


""" Module provides functionality for common gui related tasks. """


import sys
from thread import get_ident
from threading import Lock, Condition

from qt import QMimeSourceFactory, QCustomEvent, QObject, qApp, QEvent, \
               QPixmap, QApplication, QLabel, \
               QPoint, Qt, QFrame

from datafinder.core.configuration import constants
try:
    from datafinder.gui.gen import static_images
    _haveImagesAsModule = True
except ImportError:
    _haveImagesAsModule = False


__version__ = "$Revision-Id:$" 


_defaultLargeIconName = "dataType24.png"
_defaultSmallIconName = "dataType16.png"


def getPixmapForImageName(name, smallIcon=True):
    """
    Returns the pixmap for the given name.
    If the pixmap can not be found a default icons will be returned.

    @param name: Name of the image.
    @type name: C{unicode}
    @param smallIcon: Flag indicating whether a small icon (16 pixels) or a large icon (24 pixels) is required.
    @type smallIcon: C{bool}

    @return: The Qt pixmap.
    @rtype: L{QPixmap<qt.QPixmap>}
    """

    result = None
    if not name is None:
        if smallIcon:
            name += "16.png"
        else:
            name += "24.png"
        result = QPixmap.fromMimeSource(name)
    if result is None or result.isNull():
        if smallIcon:
            result = QPixmap.fromMimeSource(_defaultSmallIconName)
        else:
            result = QPixmap.fromMimeSource(_defaultLargeIconName)
    return result


def addQtImagePath(localPath):
    """
    Adds path where Qt can look for images.
    
    @param localPath: Path on the local file system.
    @type localPath: C{unicode}
    """

    QMimeSourceFactory.defaultFactory().addFilePath(localPath)


def showSplash(splashImageName):
    """
    Function which shows a nice splash screen.

    @param splashImageName: Name of the splash screen image.
    @type splashImageName: C{unicode}
    """

    screen = QApplication.desktop().screenGeometry()

    if not _haveImagesAsModule:
        addQtImagePath(constants.LOCAL_INSTALLED_ICONS_DIRECTORY_PATH)
    dfPicture = QPixmap.fromMimeSource(splashImageName)

    dfSplash = QLabel(None, "splash",
                      Qt.WDestructiveClose | Qt.WStyle_Customize | Qt.WStyle_NoBorder |\
                      Qt.WX11BypassWM | Qt.WStyle_StaysOnTop)
    dfSplash.setFrameStyle(QFrame.WinPanel | QFrame.Raised)
    dfSplash.setPixmap(dfPicture)
    dfSplash.setCaption("DataFinder")
    dfSplash.setAutoResize(1)
    dfSplash.move(QPoint(screen.center().x() - dfSplash.width() / 2,
                         screen.center().y() - dfSplash.height() / 2))
    dfSplash.show()
    dfSplash.repaint(0)
    QApplication.flush()
    return dfSplash


class CallbackEventHandler(QObject):
    """
    Allows the posting of Qt events from python threads.

    @note: initialise an instance of this class only from the Qt main thread.
    """

    def __init__(self):
        """ Constructor. """

        QObject.__init__(self)
        self.__mainThreadIdentifier = get_ident()

    def customEvent(self, event):
        """ @ see L{customEvent<QObject.customEvent>}"""

        if isinstance(event, _MyCustomEvent):
            _performCall(event.functionToCall, event.callback, event.arguments)

    def callFunctionInQtThread(self, functionToCall, blocking, *arguments):
        """
        Calls the given function in the Qt thread. If this is used from the Qt main thread
        the given function is directly called. If C{blocking} is C{True} and the method is
        not called from the Qt main thread it will be ensured that the python thread is blocked
        until the function is executed.

        @param functionToCall: Pointer to the function that has to be executed.
        @param arguments: Arguments required for the function.
        @param blocking: Blocks the calling thread.
        @type blocking: C{boolean}
        """

        if get_ident() == self.__mainThreadIdentifier: # call directly
            _performCall(functionToCall, None, arguments)
        else: # post event in the main Qt thread
            event = _MyCustomEvent(functionToCall, arguments)
            if blocking:
                conditionVar = Condition(Lock())
                conditionVar.acquire()
                def callback():
                    conditionVar.acquire()
                    conditionVar.notify()
                    conditionVar.release()
                event.callback = callback
                qApp.postEvent(self, event)
                conditionVar.wait()
                conditionVar.release()
            else:
                qApp.postEvent(self, event)


class _MyCustomEvent(QCustomEvent):
    """ A custom event class. """

    __eventIdentifier = QEvent.User # + 1000

    def __init__(self, functionToCall, arguments):
        """ Constructor. """

        QCustomEvent.__init__(self, 1000)
        self.functionToCall = functionToCall
        self.callback = None
        self.arguments = arguments


def _performCall(functionToCall, callback, arguments):
    """ Performs the function call. """

    if not functionToCall is None and not arguments is None:
        functionToCall(*arguments)
    if not callback is None:
        callback()


def binaryStringToUnicodeStringDecoding(binaryString):
    """
    Decodes the given binary string into an unicode string.
    The primarily use is for decoding file system paths.
    In order to perform the decoding the default file system encoding
    is used. If it fails on non-Windows operating systems, it will be tried
    to use the Windows encoding "cp437". This encoding is used when a
    a file name is written via a Samba share from a Windows client.
    If the given string is already an unicode string this string is returned and
    no conversion is tried.
    
    @param binaryString: String to decode.
    @type binaryString: C{string}
    
    @retrun: Unicode representation of the binary string.
    @rtype: C{unicode}
    """
    
    fileSystemEncoding = sys.getfilesystemencoding()
    if fileSystemEncoding is None:
        fileSystemEncoding = "utf-8"
    if not isinstance(binaryString, unicode):
        try:
            unicodeString = binaryString.decode(fileSystemEncoding)
        except UnicodeDecodeError:
            if sys.platform != "win32":
                unicodeString = binaryString.decode("cp437")
    else:
        unicodeString = binaryString
    return unicodeString
