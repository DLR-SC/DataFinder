# pylint: disable=W0212
# W0212: For testing it is fine to access protected members.
#
# $Filename$$
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
Test cases of the privilege dialog.
"""


import unittest 
import sys

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QApplication, QItemSelectionModel

from datafinder.core.item.privileges.principal import SPECIAL_PRINCIPALS
from datafinder.gui.user.dialogs.privilege_dialog.main import PrivilegeDialog
from datafinder_test.gui.user.dialogs.privilege_dialog.main import RepositoryMock, ItemMock


__version__ = "$Revision-Id:$" 


class PrincipalSearchTestCase(unittest.TestCase): 
    """ 
    Tests the principal search controller.
    """
    
    _application = QApplication(sys.argv)
    
    def setUp(self):
        """ Creates the test setup. """
        
        self._repositoryMock = RepositoryMock()
        self._privilegeDialog = PrivilegeDialog(self._repositoryMock)
        self._privilegeDialog.item = ItemMock()
        self._model = self._privilegeDialog._principalSearchModel
        self._controller = self._privilegeDialog._principalSearchController

        # Setup for testing the add principal interface
        self._items = list()
        self._application.connect(self._controller, 
                                  SIGNAL(self._controller.ADD_PRINCIPAL_SIGNAL), 
                                  self._addPrincipalCallback)
        
    def _addPrincipalCallback(self, items):
        """ Just add the retrieved items to C{self._items}. """
        
        self._items = items
        
    def testSearchSuccess(self):
        """ Tests the successful default search. """
        
        self._controller._searchButton.click()
        self._waitUntilFinished()
        self.assertEquals(self._model.rowCount(), 6)
        self.assertEquals(unicode(self._model.item(0, 0).text()), 
                          SPECIAL_PRINCIPALS[0].displayName) 
        self.assertEquals(self._model.item(10, 0), None) 
        self.assertEquals(self._repositoryMock.searchMode, 2)
        
    def testSearchSuccessUser(self):
        """ Tests the successful user-only search. """
        
        self._controller._userFilterButton.setChecked(True)
        self._controller._searchButton.click()
        self._waitUntilFinished()
        self.assertEquals(self._model.rowCount(), 6)
        self.assertEquals(self._repositoryMock.searchMode, 0)
        
    def testSearchSuccessGroup(self):
        """ Tests the successful group-only search. """
        
        self._controller._groupFilterButton.setChecked(True)
        self._controller._searchButton.click()
        self._waitUntilFinished()
        self.assertEquals(self._model.rowCount(), 6)
        self.assertEquals(self._repositoryMock.searchMode, 1)
        
    def _waitUntilFinished(self):
        """ Helper function which waits until the worker thread has finished. """

        while self._controller._workerThread.isRunning():
            pass
        
    def testSearchError(self):
        """ Tests the error handling of the search. """
        
        self._repositoryMock.error = True
        self._controller._searchButton.click()
        self._waitUntilFinished()
    
    def testAddPrincipal(self):
        """ Tests the adding of principals. """
        
        self._controller._addPrincipalButton.click()
        self.assertEquals(len(self._items), 0)
        
        index = self._model.index(0, 0)
        self._controller._resultWidget.selectionModel().select(index, QItemSelectionModel.SelectCurrent)
        self._controller._addPrincipalButton.click()
        self.assertEquals(len(self._items), 1)
        self.assertEquals(len(self._controller._resultWidget.selectedIndexes()), 0)
