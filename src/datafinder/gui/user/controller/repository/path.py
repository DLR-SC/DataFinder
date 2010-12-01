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
Controls the path editor view.
"""


from datafinder.gui.user.common.delegate import AbstractDelegate
from datafinder.gui.user.common import util
from datafinder.gui.user.common.controller import AbstractController


__version__ = "$Revision-Id:$" 


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
