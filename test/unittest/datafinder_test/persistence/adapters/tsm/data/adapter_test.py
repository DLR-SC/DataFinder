# pylint: disable-msg=C0103, W0201
# Created: 16.09.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: adapter_test.py 4492 2010-03-03 17:14:11Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Test cases of the TSM data adapter.
"""


import unittest
import socket
from StringIO import StringIO

from paramiko import SSHException

from datafinder.persistence.adapters.tsm.data import adapter
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4492 $"


class _ChannelMock(SimpleMock):
    """
    More specific mock for a channel instance.
    """
    
    def __init__(self, stderr="", stdout="", returnValue=None, error=None, methodNameResultMap=None):
        """ Constructor. """
        
        SimpleMock.__init__(self, returnValue, error, methodNameResultMap)
        self._stderr = StringIO(stderr)
        self.stderrRaiseTimeoutError = False 
        self._stdout = StringIO(stdout)
        self.stdoutRaiseTimeoutError = False 
        
    def recv_stderr(self, _):
        """ Mocks the receive standard error method. """
        
        if self.stderrRaiseTimeoutError:
            raise socket.timeout("")
        else:
            return self._stderr.read()
        
    def recv(self, _):
        """ Mocks the receive standard output method. """
        
        if self.stdoutRaiseTimeoutError:
            raise socket.timeout("")
        else:
            return self._stdout.read()
    
    def close(self):
        """ Mocks the close method. """
        
        pass
        
    def _setStderr(self, value):
        """ Correctly sets the standard error. """
        
        self._stderr = StringIO(value)
    stderr = property(fset=_setStderr)
    
    def _setStdout(self, value):
        """ Correctly sets the standard output. """
        
        self._stdout = StringIO(value)
    stdout = property(fset=_setStdout)

        
class _SftpClientMock(object):
    """ Mocks the used paramiko SFTPClient class. """
    
    @classmethod
    def from_transport(cls, connection): #C0103: Required to implement the mock
        """ Mocks the factory method. """
        
        return connection


class DataTsmAdapterTestCase(unittest.TestCase):
    """ Implements test cases of the data adapter. """

    def setUp(self):
        """ Creates test setup. """
        
        
        adapter.SFTPClient = _SftpClientMock
        self._channelMock = _ChannelMock()
        self._connectionMock = SimpleMock(self._channelMock)
        self._dataAdapter = adapter.DataTsmAdapter("/path/to/item", "/basPath/path/to/item", 
                                                   "serverNodeName", SimpleMock(self._connectionMock))
        
    def testFlags(self):
        """ Tests the isCollection, isLeaf and isLink flags. """
        
        self.assertFalse(self._dataAdapter.isCollection)
        self.assertFalse(self._dataAdapter.isLink)
        self.assertTrue(self._dataAdapter.isLeaf)
        self.assertFalse(self._dataAdapter.canAddChildren)
        self.assertEquals(self._dataAdapter.linkTarget, None)
    
    def testCreateCollection(self):
        """ Tests the collections creation. """
        
        self.assertRaises(PersistenceError, self._dataAdapter.createCollection, False)
        
    def testCreateLink(self):
        """ Tests the link creation. """
        
        self.assertRaises(PersistenceError, self._dataAdapter.createLink, SimpleMock())
    
    def testGetChildren(self):
        """ Tests the getChildren behavior. """
        
        self.assertRaises(PersistenceError, self._dataAdapter.getChildren)
        
    def testCreateResource(self):
        """ Tests the resource creation. """
        
        self._dataAdapter.createResource()
        
    def testExist(self):
        """ Tests the existence of the resource. """
        
        self.assertTrue(self._dataAdapter.exists())
        
        self._channelMock.stderr = "Error Code... ANS1092W kkk"
        self.assertFalse(self._dataAdapter.exists())
        
        self._channelMock.stderr = ""
        self._channelMock.stdout = "Error Code... ANS1217E kkk"
        self.assertRaises(PersistenceError, self._dataAdapter.exists)
        
        self._channelMock.stdout = ""
        self._channelMock.methodNameResultMap = {"exec_command": (None, SSHException())} #W0201: Pylint cannot see this on commit time
        self.assertRaises(PersistenceError, self._dataAdapter.exists)
        
    def testDelete(self):
        """ Tests the deletion method. """
        
        self._dataAdapter.delete()
        
        self._dataAdapter.exists = lambda: False
        self.assertRaises(PersistenceError, self._dataAdapter.delete)
        
        self._dataAdapter.exists = lambda: True
        self._channelMock.stderr = "An error occurred..."
        self.assertRaises(PersistenceError, self._dataAdapter.delete)
        
        self._channelMock.stderrRaiseTimeoutError = True
        self.assertRaises(PersistenceError, self._dataAdapter.delete)
        
    def testCopy(self):
        """ Tests the copying behavior. """

        self._dataAdapter.readData = lambda: SimpleMock()
        self._dataAdapter.copy(SimpleMock())
        
    def testMove(self):
        """ Tests the moving behavior. """
        
        self.assertRaises(PersistenceError, self._dataAdapter.move, SimpleMock())
        
    def testReadData(self):
        """ Tests the retrieving of data. """
        
        self._dataAdapter._sendCommand = lambda _, __: None
        self._connectionMock.value = StringIO("")
        self.assertEquals(self._dataAdapter.readData().read(), "")
        
        self._connectionMock.value = StringIO("Some test data...")
        self.assertEquals(self._dataAdapter.readData().read(), "Some test data...")
        
        self._dataAdapter.exists = lambda: False
        self.assertRaises(PersistenceError, self._dataAdapter.readData)
        
        self._dataAdapter.exists = lambda: True
        self._connectionMock.value = SimpleMock(error=IOError(""))
        self.assertRaises(PersistenceError, self._dataAdapter.readData)
        
        self._connectionMock.value = SimpleMock(error=SSHException(""))
        self.assertRaises(PersistenceError, self._dataAdapter.readData)
        
    def testWriteData(self):
        """ Tests the behavior of the write data method. """
        
        self._dataAdapter.exists = lambda: False
        self._dataAdapter.writeData(StringIO(""))
        
        self._dataAdapter.writeData(StringIO("Some test data to write..."))
        
        self._dataAdapter.exists = lambda: True
        self.assertRaises(PersistenceError, self._dataAdapter.writeData, StringIO(""))
        
        self._dataAdapter.exists = lambda: False
        self._connectionMock.value = SimpleMock(error=IOError(""))
        self.assertRaises(PersistenceError, self._dataAdapter.writeData, StringIO("Some test data..."))
        
        self._connectionMock.value = SimpleMock(error=SSHException(""))
        self.assertRaises(PersistenceError, self._dataAdapter.writeData, StringIO("Some test data..."))
