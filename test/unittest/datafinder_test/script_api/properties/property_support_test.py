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

from datafinder.script_api.error import ItemSupportError
from datafinder.script_api.item import item_support
from datafinder.script_api.properties import property_support
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
