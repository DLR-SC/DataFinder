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
Implements basic controller behavior of the user GUI.
"""


from PyQt4 import QtCore


__version__ = "$Revision-Id:$" 


class AbstractController(object):
    """ Abstract controller of the MVC architecture. """

    def __init__(self, widget, mainWindow=None, model=None, focusable=False, parentController=None):
        """
        Constructor.

        @param widget: The widget that is associated with this view.
        @type widget: L{QWidget<PyQt4.QtGui.QWidget>}
        @param mainWindow: Main window/widget that is contains this view.
        @type mainWindow: L{MainWindow<datafinder.gui.user.application.MainWindow}
        @param model: Model that is associated with this view.
        @type model: C{object}
        @param focusable: Enables the focusability for this view.
        @type focusable: C{bool}
        @param parentController: Parent controller of this one.
        @type parentController: L{AbstractController<datafinder.gui.user.common.controller.AbstractController>}
        """

        self.__widget = widget
        self.__mainWindow = mainWindow
        self.__model = None
        self.__focusable = focusable
        self.__focusHandler = None
        self.__parentController = parentController

        if not model is None:
            self.model = model
        if focusable:
            self._setFocusable()
            
    def _setFocusable(self):
        """
        Set the view focusable and extends the functionality of the view.

        @param focusable: True when the view has to be focusable else False.
        @type focusable: C{boolean}
        """

        if self.__focusable:
            self.__focusHandler = _FocusHandler(self.widget, self.mainWindow)
        else:
            self.__focusHandler = None
        self.emit(QtCore.SIGNAL("focusablityUpdateSignal"), self.__focusable)

    def __getattr__(self, name):
        """ Delegates to C{self.__focusHandler}. """

        try:
            return getattr(self.__focusHandler, name)
        except AttributeError:
            if hasattr(self.__widget, name):
                return getattr(self.__widget, name)
        raise AttributeError("Unknown attribute '%s'" % name)

    @property
    def widget(self):
        """ Returns the wrapped widget of this class. """

        return self.__widget

    @property
    def parentController(self):
        """ Returns the parent controller. """
        
        return self.__parentController
        
    def _getModel(self):
        """ Getter for C{self.__model}. """

        return self.__model

    def _setModel(self, model):
        """ Setter for C{self.__model}. """

        self.__model = model
        if hasattr(self, "setModel"):
            self.setModel(model)
        self.emit(QtCore.SIGNAL("modelUpdateSignal"), model)

    def _getFocusable(self):
        """ Flag indicating whether the controller can focusable. """

        return self.__focusable

    @property
    def mainWindow(self):
        """ Returns the main window in which this view is contained. """

        return self.__mainWindow

    model = property(_getModel, _setModel)


class _FocusHandler(object):
    """
    The MainWindowHandler is responsible for signaling of the current focus widget.
    """

    def __init__(self, widget, mainWindow):
        """
        Constructor.

        @param widget: The widget from which the focus event has to be catched.
        @type widget: C{QtGui.QWidget}

        @param mainWindow: The L{FocusObserver} that is responsible for the focus management.
        @type mainWindow: C{FocusObserver}
        """

        self.__mainWindow = mainWindow
        self.__widget = widget

        #Redirects the focus in event to the private method of this class.
        widget.focusInEvent = self.__focusInEvent

    def __focusInEvent(self, event):
        """
        Method will be called when the given widget was focused.
        """

        if self.__mainWindow.myFocusHandler != self and event.gotFocus():
            self.__mainWindow.myFocusHandler = self

    def focusSignal(self, focus):
        """
        Signal can be used to emit the current focus state of this view.

        @param focus: The current focus state of this view.
        @type focus: C{bool}
        """

        self.__widget.emit(QtCore.SIGNAL("focusSignal"), focus)


class FocusObserver(object):
    """
    Inherits from this class when it is necessary to allow the window to observe the
    current focus state of several L{AbstractView} object.
    """

    def __init__(self):
        """
        Constructor.
        """

        self.__focusHandler = None

    def _getFocusHandler(self):
        """
        Returns the current focus handler.

        @return: Current focus handler.
        @rtype: C{datafinder.gui.user.main_window.MainWindowHandler}
        """

        return self.__focusHandler

    def _setFocusHandler(self, handler):
        """
        Setter for the current handler that is responsible for the focus handling.
        Method will call the focousOut method of the stored handler.

        @param handler: Handler that handle all focus changes.
        @type handler: C{datafinder.gui.user.main_window.MainWindowHandler}
        """

        if self.__focusHandler != handler:
            if self.__focusHandler:
                self.__focusHandler.focusSignal(False)
            self.__focusHandler = handler
            self.__focusHandler.focusSignal(True)

    myFocusHandler = property(_getFocusHandler, _setFocusHandler)
