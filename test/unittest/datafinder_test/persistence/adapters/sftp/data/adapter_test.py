# -*- coding: utf-8 -*-
#
# $Filename$ 
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
Tests for the SFTP adapter.
"""


import errno
import StringIO
import unittest

import mock
import paramiko

from datafinder.persistence.adapters.sftp.data import adapter
from datafinder.persistence.adapters.sftp import utils
from datafinder.persistence import error


__version__ = "$Revision-Id:$" 


_STAT_IS_COLLECTION_CODE = 16895
_STAT_IS_LEAF_CODE = 1


class SftpDataAdapterTest(unittest.TestCase):
    """ Provides all unit tests for the SFTP adapter. """
    # pylint: disable=R0904
    
    def setUp(self):
        self._factoryMock = mock.Mock()
        
        self._connectionMock = mock.Mock(spec=paramiko.SFTPClient)
        self._connectionMock.open.return_value = StringIO.StringIO("Test Data")
        
        self._connectionPoolMock = mock.Mock()
        self._connectionPoolMock.acquire.return_value = self._connectionMock
        
        self._idMapper = utils.ItemIdentifierMapper(u"/bäsePath")
        
        self._sftpItem = adapter.SftpDataAdapter(
            u"/pärent/identifier", "/ppärent/pidentifier", 
            self._connectionPoolMock, self._factoryMock, self._idMapper)
        
    def testIsCollection(self):
        self._markItemAsCollection()
        
        self.assertTrue(self._sftpItem.isCollection)
        self.assertTrue(self._sftpItem.canAddChildren)
        self.assertFalse(self._sftpItem.isLeaf)
        self.assertFalse(self._sftpItem.isLink)
        
    def _markItemAsCollection(self):
        self._connectionMock.stat.return_value = mock.Mock(st_mode=_STAT_IS_COLLECTION_CODE)
        
    def testIsLeaf(self):
        self._markItemAsLeaf()
        
        self.assertTrue(self._sftpItem.isLeaf)
        self.assertFalse(self._sftpItem.isCollection)
        self.assertFalse(self._sftpItem.canAddChildren)
        self.assertFalse(self._sftpItem.isLink)
        
    def _markItemAsLeaf(self):
        self._connectionMock.stat.return_value = mock.Mock(st_mode=_STAT_IS_LEAF_CODE)
        
    def testIsNeverALink(self):
        self.assertFalse(self._sftpItem.isLink)
        
    def testCreateCollectionSuccess(self):
        self._sftpItem.createCollection()
        
        self.assertTrue(self._connectionMock.mkdir.called)
        
    def testCreateCollectionRecursivelySuccess(self):
        nonExistingParent = mock.Mock()
        nonExistingParent.exists.return_value = False
        existingParent = mock.Mock()
        self._factoryMock.createDataStorer.side_effect = [nonExistingParent, existingParent]
         
        self._sftpItem.createCollection(recursively=True)
        
        self.assertTrue(nonExistingParent.createCollection.called)
        self.assertFalse(existingParent.createCollection.called)
        self.assertTrue(self._connectionMock.mkdir.called)
        
    def testCreateCollectionRecursivelyTooDeeplyNestedCollection(self):
        parentDataStorer = adapter.SftpDataAdapter(
            u"/pärent", "/ppärent", 
            self._connectionPoolMock, self._factoryMock, self._idMapper)
        parentDataStorer.exists = mock.Mock(return_value=False)
        self._factoryMock.createDataStorer.return_value = parentDataStorer
        
        self.assertRaises(
            error.PersistenceError,
            self._sftpItem.createCollection, recursively=True)
        
    def testCreateResourceSuccess(self):
        self._sftpItem.writeData = mock.Mock()
        
        self._sftpItem.createResource()
        
        self.assertTrue(self._sftpItem.writeData.called)
        
    def testCreateLinkNotImplemented(self):
        self.assertRaises(error.PersistenceError, self._sftpItem.createLink, None)
        
    def testGetChildrenSuccess(self):
        self._connectionMock.listdir.return_value = ["a", "b", "c", "d"]
        
        self.assertEquals(len(self._sftpItem.getChildren()), 4)
        
    def testGetChildrenFromLeaf(self):
        self._connectionMock.listdir.side_effect = IOError
        
        self.assertRaises(error.PersistenceError, self._sftpItem.getChildren)
        
    def testItemExists(self):
        self.assertTrue(self._sftpItem.exists())
        
    def testItemDoesNotExist(self):
        ioError = IOError()
        ioError.errno = errno.ENOENT
        self._connectionMock.stat.side_effect = ioError 
        
        self.assertFalse(self._sftpItem.exists())
        
    def testCannotDetermineItemExistence(self):
        self._connectionMock.stat.side_effect = IOError 
        
        self.assertRaises(error.PersistenceError, self._sftpItem.exists)
        
    def testDeleteLeafSuccess(self):
        self._markItemAsLeaf()
        
        self._sftpItem.delete()
        
    def testDeleteLeafThatDoesNotExist(self):
        self._markItemAsLeaf()
        self._connectionMock.remove.side_effect = IOError
        
        self.assertRaises(error.PersistenceError, self._sftpItem.delete)
        
    def testDeleteCollectionSuccess(self):
        self._markItemAsCollection()
        self._defineSubCollectionStructure()
        
        self._sftpItem.delete()
        
        self.assertEquals(self._connectionMock.rmdir.call_count, 3)
        
    def _defineSubCollectionStructure(self):
        leaf1 = mock.Mock(st_mode=_STAT_IS_LEAF_CODE, filename="ä1")
        leaf2 = mock.Mock(st_mode=_STAT_IS_LEAF_CODE, filename="ä2")
        col1 = mock.Mock(st_mode=_STAT_IS_COLLECTION_CODE, filename="c1")
        col2 = mock.Mock(st_mode=_STAT_IS_COLLECTION_CODE, filename="c2")
        self._connectionMock.listdir_attr.side_effect = [[col1, col2], [leaf1], [leaf2]]
        
    def testDeleteCollectionWhichDoesNotExist(self):
        self._markItemAsCollection()
        self._connectionMock.listdir_attr.side_effect = IOError
        
        self.assertRaises(error.PersistenceError, self._sftpItem.delete)
        
    def testCopyLeafSuccess(self):
        self._markItemAsLeaf()
        
        destination = mock.Mock(identifier=u"/newDästination")
        self._sftpItem.copy(destination)
        
    def testCopyLeafThatDoesNotExist(self):
        self._markItemAsLeaf()
        self._sftpItem.readData = mock.Mock(side_effect=error.PersistenceError)
        
        destination = mock.Mock(identifier=u"/newDästination")
        self.assertRaises(error.PersistenceError, self._sftpItem.copy, destination)
        
    def testCopyCollectionSuccess(self):
        # pylint: disable=R0201,C0111
        # we do have to worry about such small fake implementations        
        # pylint: disable=W0212
        # access to prtected member ok for testing
        
        self._markItemAsCollection()
        self._defineSubCollectionStructure()
        class _FactoryMock(object):
            def createDataStorer(self, identifier):
                return mock.Mock(identifier=identifier)
        self._sftpItem._factory = _FactoryMock()
            
        destination = mock.Mock(identifier=u"/newDästination")
        self._sftpItem.copy(destination)
    
    def testCopyCollectionWhichDoesNotExist(self):
        self._markItemAsCollection()
        self._connectionMock.listdir_attr.side_effect = IOError
        
        destination = mock.Mock(identifier=u"/newDästination")
        self.assertRaises(error.PersistenceError, self._sftpItem.copy, destination)
        
    def testMoveSuccess(self):
        destination = mock.Mock(identifier=u"/newDästination")
        self._sftpItem.move(destination)
        
        self.assertTrue(self._connectionMock.rename.called)
        
    def testMoveNonExistingItem(self):
        self._connectionMock.rename.side_effect = IOError
        
        destination = mock.Mock(identifier=u"/newDästination")
        self.assertRaises(error.PersistenceError, self._sftpItem.move, destination)
        
    def testWriteSuccess(self):
        data = StringIO.StringIO("Test Data")
        self._sftpItem.writeData(data)
        
        self.assertTrue(self._connectionMock.open.called)
        self.assertTrue(data.closed)
    
    def testWriteEnsureEmptyFileIsCreated(self):
        self._sftpItem.writeData(StringIO.StringIO(""))
        
        self.assertTrue(self._connectionMock.open.called) 
        
    def testWriteNoSuchFile(self):
        self._connectionMock.open.side_effect = IOError
        
        self.assertRaises(
            error.PersistenceError,
            self._sftpItem.writeData, StringIO.StringIO(""))

    def testReadSuccess(self):
        fileObject = self._sftpItem.readData()
        
        self.assertEquals(fileObject.read(), "Test Data")
        self.assertTrue(self._connectionMock.open.called)
        
    def testReadNoSuchFile(self):
        self._connectionMock.open.side_effect = IOError
        
        self.assertRaises(error.PersistenceError, self._sftpItem.readData)
    