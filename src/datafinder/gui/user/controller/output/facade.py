# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
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
This module contains the OutputFacadeController. The OutputFacadeController is responsible for the initialization of
all component of the output view of the DataFinder User Client.
That contains the general output view which is responsible for the visibility of the tabs and
the L{QtGui.QTabWidget}.
The OutputFacadeController has to provide all interfaces that are necessary to interact with the output
part of the DataFinder User Client.
"""


from PyQt4 import QtCore

from datafinder.gui.user.common import util
from datafinder.gui.user.common.delegate import AbstractDelegate
from datafinder.gui.user.common.controller import AbstractController
from datafinder.gui.user.controller.output.logger import LoggingTableController
from datafinder.gui.user.controller.output.searchresults import SearchResultController


__version__ = "$Revision-Id:$" 


class OutputFacadeController(AbstractController):
    """
    The OutputFacadeController initializes all members of the output part of the DataFinder User Client.
    """

    def __init__(self, mainWindow, searchModel, itemActionController):
        """ Constructor. """

        AbstractController.__init__(self, mainWindow.outputTabWidget, mainWindow)
        
        self._searchModel = searchModel
        self.__rootLogController = LoggingTableController(mainWindow.rootLogTableView, self)
        self.__scriptLogController = LoggingTableController(mainWindow.scriptLogTableView, self)
        self.__resultController = SearchResultController(mainWindow.searchResultTableView, mainWindow, 
                                                         self, itemActionController)
        self.__resultController.model = searchModel
        
        self.__properties = dict(myRootLogView=self.__rootLogController,
                                 myScriptLogView=self.__scriptLogController,
                                 myResultView=self.__resultController)

        self._delegates = [OutputDelegate(self)]
        self.connect(self._searchModel, QtCore.SIGNAL("updateSignal"), self.updateSlot)
        self.connect(mainWindow.outputTabWidget, QtCore.SIGNAL("currentChanged(int)"), self._currentTabChanged)
        
        self.fetchTabs()
        
    def __getattr__(self, name):
        """
        Returns the internal attribute referenced under the given name.

        @param name: Name of the attribute that has to be returned.
        @type name: C{unicode}
        """

        if self.__properties.has_key(name):
            return self.__properties[name]
        return AbstractController.__getattr__(self, name)

    def updateSlot(self):
        """
        Slot is called when a search was successfully performed.
        """

        self.setCurrentIndex(2)
        self._displayNumberOfSearchResults(2)

    def _displayNumberOfSearchResults(self, index):
        """ Display the number of search results in the status bar. """

        self.mainWindow.statusBar().clearMessage()
        rowCount = self._searchModel.rowCount()
    
        if rowCount > 0 and index == 2:
            statusMessage = "%i items have been found." % rowCount
            self.mainWindow.statusBar().showMessage(statusMessage)
    
    def _currentTabChanged(self, index):
        """ Sets search result number in the status bar when the search results tab is shown. """
        
        self._displayNumberOfSearchResults(index)


class OutputDelegate(AbstractDelegate):
    """
    Handles signals of the output area.
    """

    def __init__(self, controller):
        """ Constructor. """

        AbstractDelegate.__init__(self, controller)
        
    @util.immediateConnectionDecorator("logAction", "triggered(bool)")
    def _showLogsSlot(self, showIt):
        """ Sets the correct tab for the logging messages. """

        self._controller.setTabShown(0, showIt)

    @util.immediateConnectionDecorator("scriptOutputAction", "triggered(bool)")
    def _showScriptOutputSlot(self, showIt):
        """ Sets the correct tab for the logging messages. """

        self._controller.setTabShown(1, showIt)

    @util.immediateConnectionDecorator("searchResultsAction", "triggered(bool)")
    def _showSearchResultsSlot(self, showIt):
        """ Sets the correct tab for the search results. """

        self._controller.setTabShown(2, showIt)
