#
# Created: 10.02.2010 Patrick Schaefer <patrick.schaefer@dlr.de>
#
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


"""
Test case for the item support module.
"""


import unittest

from datafinder.script_api.error import ItemSupportError
from datafinder.script_api.item import item_support
from datafinder.script_api.properties import property_support
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4556 $"


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
        property_support.repositoryManagerInstance = self._repositoryManagerInstanceMock
        self._createItemMock = SimpleMock()
        item_support.__createItem = self._createItemMock
        
    def testRetrieveProperties(self):
        """ Tests for the retrieveProperties method. """

        self._itemMock.properties = dict()
        property_support.retrieveProperties("")
        
        self._repositoryMock.error = ItemSupportError("")
        self.assertRaises(ItemSupportError, property_support.retrieveProperties, "")

    def testStoreProperties(self):
        """ Tests for the storeProperties method. """

        property_support.storeProperties("", dict())
        
        self._itemMock.error = ItemSupportError("")
        self.assertRaises(ItemSupportError, property_support.storeProperties, "", dict())

    def testDeleteProperties(self):
        """ Tests for the deleteProperties method. """

        property_support.deleteProperties("", list())
        
        self._itemMock.error = ItemSupportError("")
        self.assertRaises(ItemSupportError, property_support.deleteProperties, "", list())
