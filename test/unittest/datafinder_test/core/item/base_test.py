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

from datafinder.core.item.base import ItemBase
from datafinder.core.item.collection import ItemRoot, ItemCollection
from datafinder.core.item.data_persister.constants import ITEM_STATE_NULL
from datafinder.core.item.leaf import ItemLeaf
from datafinder.core.item.privileges.privilege import ALL_PRIVILEGE
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4466 $"


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
    