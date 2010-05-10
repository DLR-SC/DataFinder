#
# reading and storage of preferences of current session
#
# Created: Malte Legenhausen (mail to malte.legenhausen@dlr.de)
#
# Version: $Id
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
Test case for the ItemBase class.
"""


import unittest

from datafinder.core.item.collection import ItemCollection
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 3962 $"


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
