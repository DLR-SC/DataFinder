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
Tests of inherited privilege handling.
"""


import unittest
import sys

from PyQt4.QtGui import QApplication

from datafinder.core.item.privileges.principal import SPECIAL_PRINCIPALS
from datafinder.gui.user.dialogs.privilege_dialog.main import PrivilegeDialog
from datafinder_test.gui.user.dialogs.privilege_dialog.main import PrivilegeItemMock, PrivilegeRepositoryMock


__version__ = "$Revision-Id:$" 


class InheritedPrivilegeControllerTest(unittest.TestCase):
    """ Tests of the inherited privileges controller. """

    _application = QApplication(sys.argv)
    
    def setUp(self):
        """ Creates the privilege dialog and all required mocks. """
        
        # Setup repository
        # "/" -> 2 principals, "/test" -> no principals 
        selectedItem = PrivilegeItemMock("/test/test.pdf", None)
        self._repositoryMock = PrivilegeRepositoryMock([selectedItem])
        rootItem = self._repositoryMock.nodeFromPath("/")
        rootItem.acl.addDefaultPrincipal(SPECIAL_PRINCIPALS[1])
        middleItem = self._repositoryMock.nodeFromPath("/test")
        middleItem.acl.clearPrivileges(SPECIAL_PRINCIPALS[0])

        # Creating the dialog        
        self._privilegeDialog = PrivilegeDialog(self._repositoryMock)
        self._privilegeDialog.item = selectedItem
        self._principalController = self._privilegeDialog._principalSearchController
        self._model = self._privilegeDialog._inheritedPrivilegesModel
        self._controller = self._privilegeDialog._inheritedPrivilegesController
        
        # Checking model content
        self.assertEquals(self._model.rowCount(), 2)
        
    def testPrivilegeSelection(self):
        """ Tests correct handling of privilege table selection. """

        # Selecting existing rows
        self._controller._privilegeWidget.selectRow(0)
        self.assertFalse(self._controller._selectItemWidget.hasEmptySelection)
        self._controller._privilegeWidget.selectRow(1)
        self.assertEquals(unicode(self._controller._selectItemWidget.pathLineEdit.text()), "/")
        
        # Selecting non-existing row
        self._controller._privilegeWidget.selectRow(2)
        self._controller._privilegeWidget.selectionModel().clear()
        self.assertFalse(len(self._controller._privilegeWidget.selectedIndexes()) > 0)
        self.assertEquals(unicode(self._controller._selectItemWidget.pathLineEdit.text()), "/")
         
    def testTreeSelection(self):
        """ Tests correct handling of selections in the item tree. """
        
        # Testing initial selection of the root item
        self.assertEquals(len(self._controller._privilegeWidget.selectedIndexes()), 8)
        
        # Testing selection of the middle item with no table entries
        index = self._repositoryMock.indexFromPath("/test")
        self._controller._selectItemWidget.selectedIndexes = [index]
        self.assertEquals(unicode(self._controller._selectItemWidget.pathLineEdit.text()), "/test")
        self.assertEquals(len(self._controller._privilegeWidget.selectedIndexes()), 0)
        
    def testEdit(self):
        """ Tests the editing of an inherited item. """
        
        self._controller._privilegeWidget.selectRow(0)
        self._controller._editButton.click()
        self.assertEquals(len(self._model._itemRowMap), 0)
        self.assertEquals(self._privilegeDialog.item.path, "/")
