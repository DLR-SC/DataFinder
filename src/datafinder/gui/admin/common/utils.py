# pylint: disable-msg=R0201, W0142, W0611
# R0201: CallbackEventHandler.customEvent is required to be a method. Overwrites default implementation of QObject.
# W0142: Required because this is the way to call function with unspecified argument list.
# W0611: Here the import of the module performs all the work.
#
# Initialization and administration of DataFinder images.
#
# Created: Tobias Schlauch (tobias.schlauch@dlr.de)
#
# Version: $Id: utils.py 3926 2009-04-09 12:09:51Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


""" Module provides functionality for common gui related tasks. """


import sys
from thread import get_ident
from threading import Lock, Condition

from qt import QMimeSourceFactory, QCustomEvent, QObject, qApp, QEvent, \
               QPixmap, QApplication, QLabel, \
               QPoint, Qt, QFrame

from datafinder.core.configuration import constants
try:
    from datafinder.gui import static_images
    _haveImagesAsModule = True
except ImportError:
    _haveImagesAsModule = False


__version__ = "$LastChangedRevision: 3926 $"


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
