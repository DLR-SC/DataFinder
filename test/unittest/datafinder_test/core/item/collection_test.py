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
Test case for the ItemBase class.
"""


import unittest

from datafinder.core.item.collection import ItemCollection
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class ItemCollectionTestCase(unittest.TestCase):
    """
    Test cases for the CollectionItem.
    """

    def testGetChildren(self):
        """
        Test for the getChildren method.
        """

        collection = ItemCollection("collection")
        collection.itemFactory = SimpleMock(SimpleMock(list()))
        parent = SimpleMock(list(), isLeaf=False, isLink=False)
        parent.path = "/"
        collection.parent = parent 
        self.assertTrue(len(collection.getChildren()) == 0)

        item = ItemCollection("subitem")
        item.itemFactory = SimpleMock(SimpleMock())
        collection.addChild(item)
        self.assertTrue(len(collection.getChildren()) == 1)

    def testAddChild(self):
        """
        Test for the addChild method.
        """

        collection = ItemCollection("collection")
        collection.itemFactory = SimpleMock(SimpleMock(list()))
        parent = SimpleMock(list(), isLeaf=False, isLink=False)
        parent.path = "/"
        collection.parent = parent 
        self.assertTrue(len(collection.getChildren()) == 0)

        item = ItemCollection("subitem")
        item.itemFactory = SimpleMock(SimpleMock())
        collection.addChild(item)

        self.assertTrue(item in collection.getChildren())

    def testRemoveChild(self):
        """
        Test for the removeChild method.
        """

        collection = ItemCollection("collection")
        collection.itemFactory = SimpleMock(SimpleMock(list()))
        parent = SimpleMock(list(), isLeaf=False, isLink=False)
        parent.path = "/"
        collection.parent = parent 
        self.assertTrue(len(collection.getChildren()) == 0)

        item = ItemCollection("subitem")
        item.itemFactory = SimpleMock(SimpleMock())
        collection.addChild(item)
        self.assertTrue(item in collection.getChildren())

        collection.removeChild(item)
        self.assertTrue(len(collection.getChildren()) == 0)

    def testIsLeaf(self):
        """
        Test for the isLeaf method.
        """

        collection = ItemCollection("collection")
        self.assertFalse(collection.isLeaf)
