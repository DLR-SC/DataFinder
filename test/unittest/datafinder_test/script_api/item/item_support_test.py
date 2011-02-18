# $Filename$ 
# $Authors$
#
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
Test case for the item support module.
"""


import unittest

from datafinder.core.error import ItemError
from datafinder.script_api.error import ItemSupportError
from datafinder.script_api.item import item_support
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class ItemSupportTestCase(unittest.TestCase):
    """
    The TestCase for the item support.
    """
    
    def setUp(self):
        """ Creates the required mocks. """
        
        self._targetItemMock = SimpleMock()
        self._itemMock = SimpleMock()
        self._repositoryMock = SimpleMock(self._itemMock)
        self._repositoryManagerInstanceMock = SimpleMock(workingRepository=self._repositoryMock)
        item_support.repositoryManagerInstance = self._repositoryManagerInstanceMock
        self._createItemMock = SimpleMock()
        item_support._createItem = self._createItemMock
        
    def testRefresh(self):
        """ Test for the refresh method. """

        item_support.refresh("")
        
        self._itemMock.error = ItemError("")
        self.assertRaises(ItemSupportError, item_support.refresh, "")

    def testCreateCollection(self):
        """ Test for the createCollection method. """
        
        item_support.createCollection("", dict())
        
        self._itemMock.methodNameResultMap = {"create": (None, ItemError(""))}
        self.assertRaises(ItemSupportError, item_support.createCollection, "", dict())
    
    def testCreateLeaf(self):
        """ Test for the createLeaf method. """
        
        item_support.createLeaf("", dict())
        
        self._itemMock.methodNameResultMap = {"create": (None, ItemError(""))}
        self.assertRaises(ItemSupportError, item_support.createLeaf, "", dict())
    
    def testCreateLink(self):
        """ Test for the createLink method. """

        item_support.createLink("", "")
        
        self._itemMock.methodNameResultMap = {"create": (None, ItemError(""))}
        self.assertRaises(ItemSupportError, item_support.createLink, "", "")

    def testDelete(self):
        """ Test for the delete method. """

        item_support.delete("")
        
        self._itemMock.error = ItemError("")
        self.assertRaises(ItemSupportError, item_support.delete, "")
        
    def testCopy(self):
        """ Test for the copy method. """
        
        item_support.copy("", "")
        
        self._repositoryMock.error = ItemError("")
        self.assertRaises(ItemSupportError, item_support.copy, "", "")
        
        self._repositoryMock.error = None
        self._itemMock.methodNameResultMap = {"copy": (None, ItemError(""))}
        self.assertRaises(ItemSupportError, item_support.copy, "", "")
    
    def testMove(self):
        """ Test for the move method. """
        
        item_support.move("", "")
        
        self._repositoryMock.error = ItemError("")
        self.assertRaises(ItemSupportError, item_support.move, "", "")
        
        self._repositoryMock.error = None
        self._itemMock.methodNameResultMap = {"move": (None, ItemError(""))}
        self.assertRaises(ItemSupportError, item_support.move, "", "")

    def testRetrieveData(self):
        """ Test for the retrieveData method. """
        
        item_support.retrieveData("")

        self._itemMock.error = ItemError("")
        self.assertRaises(ItemSupportError, item_support.retrieveData, "")
        
    def testStoreData(self):
        """ Test for the storeData method. """
        
        item_support.storeData("", "")
        
        self._itemMock.error = ItemError("")
        self.assertRaises(ItemSupportError, item_support.storeData, "", "")
        
    def testSearch(self):
        """ Test for the search method. """
        
        self._itemMock.value = list()
        item_support.search("", "")

        self._itemMock.error = ItemError("")
        self.assertRaises(ItemSupportError, item_support.search, "", "")

    def testWalk(self):
        """ Tests the walk method. """

        self._repositoryMock.value = [SimpleMock(path="/"), SimpleMock(path="/test")]
        self.assertEquals(item_support.walk("/"), ["/", "/test"])
        
        self._repositoryMock.error = ItemError("")
        self.assertRaises(ItemSupportError, item_support.walk, "")
