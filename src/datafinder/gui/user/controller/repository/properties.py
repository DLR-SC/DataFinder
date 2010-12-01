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
Controller of the property view.
"""


from PyQt4 import QtCore

from datafinder.gui.user.common.delegate import AbstractDelegate
from datafinder.gui.user.common import util
from datafinder.gui.user.common.controller import AbstractController


__version__ = "$Revision-Id:$" 


class PropertiesController(AbstractController):
    """
    Controls the property view.
    """

    def __init__(self, mainWindow, parentController):
        """
        Constructor.
        """

        AbstractController.__init__(self, mainWindow.serverAttributeTableView, mainWindow, parentController=parentController)
        
        self.horizontalHeader().setSortIndicator(0, QtCore.Qt.AscendingOrder)

        self._delegates = [_PropertiesDelegate(self)]
        

class _PropertiesDelegate(AbstractDelegate):
    """
    This delegate is responsible for all user interaction with the view.
    """

    def __init__(self, controller):
        """
        Constructor.
        """

        AbstractDelegate.__init__(self, controller)

    @util.immediateConnectionDecorator("widget", "modelUpdateSignal")
    def _setSortingEnabled(self):
        """ Enables the sorting behavior. """

        self._controller.setSortingEnabled(True)
   
    @util.immediateConnectionDecorator(["serverTableSelectionModel", "serverTreeSelectionModel"],
                                        "currentChanged(QModelIndex, QModelIndex)")
    def _propertySelectionSlot(self, index, __):
        """
        Slot is called when a item was selected in the tree/table or list view.

        @param index: The selected index.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        if index.isValid():
            try:
                index = index.model().mapToSource(index)
            except AttributeError:
                index = index
            node = index.model().nodeFromIndex(index)
            self._controller.model.itemIndex = index
            self._mainWindow.serverPropertiesDockWidget.setWindowTitle("Properties of %s" % node.name)
        else:
            self._mainWindow.serverPropertiesDockWidget.setWindowTitle("Properties")

    @util.immediateConnectionDecorator("model", "modelReset()")
    def _modelResetSlot(self):
        """ Handles the reset signal of the property model. """
        
        self._mainWindow.serverPropertiesDockWidget.setWindowTitle("Properties")
