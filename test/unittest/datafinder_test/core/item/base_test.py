# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#
#met:
#
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
Test case for the ItemBase class.
"""


import unittest

from datafinder.core.item.base import ItemBase
from datafinder.core.item.collection import ItemRoot, ItemCollection
from datafinder.core.item.data_persister.constants import ITEM_STATE_NULL
from datafinder.core.item.leaf import ItemLeaf
from datafinder.core.item.privileges.privilege import ALL_PRIVILEGE
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class ItemBaseTestCase(unittest.TestCase):
    """
    The TestCase for the ItemBase.
    """

    @staticmethod
    def _createItem(name, root=None, itemType=ItemBase):
        """ Constructs an item with the given name. """
        
        item = itemType(name)
        item._privileges = [ALL_PRIVILEGE]
        item.itemFactory = SimpleMock(SimpleMock(True, affectedItems=list()))
        if not root is None:
            item.parent = root
        item._fileStorer = SimpleMock(dict())
        item._dataPersister = SimpleMock(state=ITEM_STATE_NULL)
        return item
    
    def testPropertyParent(self):
        """
        Test for the parent property.
        """
        
        root = self._createItem("", itemType=ItemRoot)
        root.path = "/"
        item = self._createItem("item", root)

        self.assertTrue(item.parent == root)
        self.assertTrue(item.path == "/item")

    def testCopy(self):
        """
        Test for the copy method.
        """

        root = self._createItem("", itemType=ItemRoot)
        root.path = "/"
        item = self._createItem("item", root)
        collection = self._createItem("collection", root, itemType=ItemCollection)
        targetItem = self._createItem("target", collection, itemType=ItemLeaf)
        
        item.copy(targetItem)
        self.assertTrue(targetItem.parent == collection)

    def testMove(self):
        """
        Test for the move method.
        """

        root = self._createItem("", itemType=ItemRoot)
        root.path = "/"
        item = self._createItem("item", root, itemType=ItemLeaf)
        collection = self._createItem("collection", root, itemType=ItemCollection)
        targetItem = self._createItem("target", collection)

        item.move(targetItem)
        self.assertTrue(targetItem.parent == collection)
        self.assertTrue(item.parent == None)
        
    def testDelete(self):
        """
        Test for the delete method.
        """

        root = self._createItem("", itemType=ItemRoot)
        root.path = "/"
        item = self._createItem("item", root, itemType=ItemLeaf)

        item.delete()
        self.assertTrue(item.parent == None)
    