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
Tests of privilege definition aspects.
"""


import unittest
import sys

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QApplication

from datafinder.core.item.privileges.principal import SPECIAL_PRINCIPALS
from datafinder.core.item.privileges.privilege import READ_ONLY_ACCESS_LEVEL, NONE_ACCESS_LEVEL
from datafinder.gui.user.dialogs.privilege_dialog.items import PrincipalItem
from datafinder.gui.user.dialogs.privilege_dialog.main import PrivilegeDialog
from datafinder_test.gui.user.dialogs.privilege_dialog.main import ItemMock


__version__ = "$Revision-Id:$" 


class PrivilegeControllerTest(unittest.TestCase):
    """ Tests of privilege controller. """

    _application = QApplication(sys.argv)
    _testPrincipalItems = [PrincipalItem(principal) for principal in SPECIAL_PRINCIPALS]
    
    def setUp(self):
        """ Creates the test fixture. """
        
        self._privilegeDialog = PrivilegeDialog(None)
        self._privilegeDialog.item = ItemMock(None)
        self._principalController = self._privilegeDialog._principalSearchController
        self._model = self._privilegeDialog._privilegeModel
        self._controller = self._privilegeDialog._privilegeController

    def testAddPrincipals(self):
        """ Tests the addition of a list of principals """
        
        # Tests adding of three principals whereby one already exists
        self.assertEquals(self._model.rowCount(), 1)
        self.assertEquals(self._controller._applyButton.isEnabled(), False)
        self._addTestPrincipals()
        for count in range(3):
            item = self._model.itemFromIndex(self._model.index(2, count))
            if count == 0:
                self.assertEquals(item.principal, SPECIAL_PRINCIPALS[2])
            elif count == 1 or count == 2:
                self.assertEquals(unicode(item.text()), READ_ONLY_ACCESS_LEVEL.displayName)
            else:
                self.assertEquals(unicode(item.text()), NONE_ACCESS_LEVEL.displayName)
        self.assertEquals(self._controller._applyButton.isEnabled(), True)

        # Ensuring that there are no duplicate principal entries
        self._addTestPrincipals()

    def _addTestPrincipals(self):
        """ Adds three test principals. """

        self._principalController.emit(SIGNAL(self._principalController.ADD_PRINCIPAL_SIGNAL), self._testPrincipalItems)
        self.assertEquals(self._controller._applyButton.isEnabled(), True)
        self.assertEquals(self._model.rowCount(), 3)

    def testRemovePrincipal(self):
        """ Tests the removal of principals. """

        # Testing removal with no selection
        self.assertEquals(self._model.rowCount(), 1)
        self.assertEquals(self._controller._applyButton.isEnabled(), False)
        self.assertEquals(self._controller._removeButton.isEnabled(), False)
        
        # Testing removal of one principal
        self._removeRow(0)
        self.assertEquals(self._model.rowCount(), 0)
        self.assertEquals(self._controller._applyButton.isEnabled(), True)
        self.assertEquals(len(self._model._acl.principals), 0)
        
        # Adding three principals
        self._addTestPrincipals()

        # Removing the last two so the start state is reached
        self._removeRow(2)
        self._removeRow(1)
        self.assertEquals(self._model.rowCount(), 1)
        self.assertEquals(self._controller._applyButton.isEnabled(), False)
        
    def _removeRow(self, row):
        """ Removes a row. """
        
        self._selectRow(row)
        self._controller._removeButton.click()
    
    def _selectRow(self, row):
        """ Selects the given row. """

        self._controller._privilegeWidget.selectRow(row)

    def testButtonEnabledStates(self):
        """ Tests the enabled state of the controlled buttons. """
        
        # Checks the initial button enabling state
        self.assertEquals(self._model.rowCount(), 1)
        self.assertEquals(self._controller._applyButton.isEnabled(), False)
        self.assertEquals(self._controller._removeButton.isEnabled(), False)
        self.assertEquals(self._controller._upButton.isEnabled(), False)
        self.assertEquals(self._controller._downButton.isEnabled(), False)
        
        # Adds and selects different entries and checks the enabling state again
        self._addTestPrincipals()
        self.assertEquals(self._controller._removeButton.isEnabled(), False)
        self.assertEquals(self._controller._upButton.isEnabled(), False)
        self.assertEquals(self._controller._downButton.isEnabled(), False)
        self._selectRow(0)
        self.assertEquals(self._controller._upButton.isEnabled(), False)
        self.assertEquals(self._controller._downButton.isEnabled(), True)
        self._selectRow(2)
        self.assertEquals(self._controller._upButton.isEnabled(), True)
        self.assertEquals(self._controller._downButton.isEnabled(), False)
        self._selectRow(1)
        self.assertEquals(self._controller._upButton.isEnabled(), True)
        self.assertEquals(self._controller._downButton.isEnabled(), True)

        # Creates the initial state and checks again the enabling state of buttons
        self._removeRow(2)
        self._removeRow(1)
        self.assertEquals(self._controller._applyButton.isEnabled(), False)
        self.assertEquals(self._controller._removeButton.isEnabled(), False)
        
    def testChangePosition(self):
        """ Tests the changing of principal positions. """
        
        # Adding three principals and selecting the second entry 
        self._addTestPrincipals()
        self._controller._applyButton.click()
        self._waitUntilFinished()
        self.assertFalse(self._model.isDirty)
        principal = SPECIAL_PRINCIPALS[1]
        self._selectRow(1)
        
        # Move the second entry up and down
        self._controller._upButton.click()
        self.assertEquals(self._model.item(0).principal, principal)
        self.assertTrue(self._model.isDirty)
        
        self._controller._downButton.click()
        self.assertEquals(self._model.item(1).principal, principal)
        self.assertFalse(self._model.isDirty)
        
        self._controller._downButton.click()
        self.assertEquals(self._model.item(2).principal, principal)
        self.assertTrue(self._model.isDirty)
        
    def _waitUntilFinished(self):
        """ Helper function which waits until the worker thread has finished. """

        while self._controller._workerThread.isRunning():
            pass
        self._controller._applyCallback()

    def testApplySuccess(self):
        """ Tests the successful apply behavior. """
        
        self._addTestPrincipals()
        self._privilegeDialog.item.error = None
        self._controller._applyButton.click()
        self._waitUntilFinished()
        self.assertFalse(self._model.isDirty)

    def testApplyError(self):
        """ Tests apply error handling. """
        
        self._privilegeDialog.item = ItemMock()
        self._addTestPrincipals()
        self._controller._applyButton.click()
        self._waitUntilFinished()
        self.assertTrue(self._model.isDirty)

    def testEditAccessLevel(self):
        """ Tests the privilege editing functionality. """
        
        itemDelegate = self._controller._privilegeWidget.itemDelegate()
        
        # Nothing should happen when trying to edit the principal
        index = self._model.index(0, 0)
        editor = itemDelegate.createEditor(None, None, index)
        self.assertEquals(editor, None)
        
        # Checking an invalid index
        index = self._model.index(10, 200)
        editor = itemDelegate.createEditor(None, None, index)
        self.assertEquals(editor, None)
        
        # Checking the three access levels
        for column in range(1, 4):
            index = self._model.index(0, column)
            editor = itemDelegate.createEditor(None, None, index)
            editor.setCurrentIndex(0)
            itemDelegate.setModelData(editor, None, index)
            self.assertEquals(self._model.item(0, column).text(), editor.currentText())
