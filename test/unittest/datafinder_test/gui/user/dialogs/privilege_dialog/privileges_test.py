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
from PyQt4.QtGui import QApplication, QItemSelectionModel

from datafinder.core.item.privileges.acl import AccessControlList
from datafinder.core.item.privileges.principal import SPECIAL_PRINCIPALS
from datafinder.core.item.privileges.privilege import READ_ONLY_ACCESS_LEVEL, NONE_ACCESS_LEVEL
from datafinder.gui.user.dialogs.privilege_dialog.items import PrincipalItem
from datafinder.gui.user.dialogs.privilege_dialog.main import PrivilegeDialog


__version__ = "$Revision-Id:$" 


class PrivilegeControllerTest(unittest.TestCase):
    """ Tests of privilege controller. """

    _application = QApplication(sys.argv)
    _testPrincipalItems = [PrincipalItem(principal) for principal in SPECIAL_PRINCIPALS]
    
    def setUp(self):
        """ Creates the test fixture. """
        
        self._privilegeDialog = PrivilegeDialog(None)
        self._privilegeDialog.item = _ItemMock()
        self._principalController = self._privilegeDialog._principalSearchController
        self._model = self._privilegeDialog._privilegeModel
        self._controller = self._privilegeDialog._privilegeController

    def testAddPrincipals(self):
        """ Tests the addition of a list of principals """
        
        # Tests adding of three principals whereby one already exists
        self.assertEquals(self._model.rowCount(), 1)
        self.assertEquals(self._controller._applyButton.isEnabled(), False)
        self._principalController.emit(SIGNAL(self._principalController.ADD_PRINCIPAL_SIGNAL), self._testPrincipalItems)
        self.assertEquals(self._model.rowCount(), 3)
        for count in range(3):
            item = self._model.itemFromIndex(self._model.index(2, count))
            if count == 0:
                self.assertEquals(item.principal, SPECIAL_PRINCIPALS[2])
            elif count == 1 or count == 2:
                self.assertEquals(item.level, READ_ONLY_ACCESS_LEVEL)
            else:
                self.assertEquals(item.level, NONE_ACCESS_LEVEL)
        self.assertEquals(self._controller._applyButton.isEnabled(), True)

        # Ensuring that there are no duplicate principal entries
        self._principalController.emit(SIGNAL(self._principalController.ADD_PRINCIPAL_SIGNAL), self._testPrincipalItems)
        self.assertEquals(self._model.rowCount(), 3)

    def testRemovePrincipal(self):
        """ Tests the removal of principals. """

        # Testing removal with no selection
        self.assertEquals(self._model.rowCount(), 1)
        self.assertEquals(self._controller._applyButton.isEnabled(), False)
        self._controller._removeButton.click()
        self.assertEquals(self._model.rowCount(), 1)
        self.assertEquals(self._controller._applyButton.isEnabled(), False)
        
        # Testing removal of one principal
        self._removeRow(0)
        self.assertEquals(self._model.rowCount(), 0)
        self.assertEquals(self._controller._applyButton.isEnabled(), True)
        self.assertEquals(len(self._model._acl.principals), 0)
        
        # Adding three principals
        self._principalController.emit(SIGNAL(self._principalController.ADD_PRINCIPAL_SIGNAL), self._testPrincipalItems)
        self.assertEquals(self._model.rowCount(), 3)
        self.assertEquals(self._controller._applyButton.isEnabled(), True)

        # Removing the last two so the start state is reached
        self._removeRow(2)
        self._removeRow(1)
        self.assertEquals(self._model.rowCount(), 1)
        self.assertEquals(self._controller._applyButton.isEnabled(), False)
        
    def _removeRow(self, row):
        """ Removes a row. """
        
        index = self._model.index(row, 0)
        self._controller._privilegeWidget.selectionModel().select(index, QItemSelectionModel.SelectCurrent)
        self._controller._removeButton.click()


class _ItemMock(object):
    """ Used to mock an item and its ACL. """
    
    def __init__(self):
        """ Constructor. """
        
        self.path = "/test/item/test.pdf"
        self.acl = AccessControlList()
        self.acl.addDefaultPrincipal(SPECIAL_PRINCIPALS[0])
