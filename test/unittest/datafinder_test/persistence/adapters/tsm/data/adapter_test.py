# pylint: disable=C0103, W0201
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
Test cases of the TSM data adapter.
"""


import unittest
import socket
from StringIO import StringIO

from paramiko import SSHException

from datafinder.persistence.adapters.tsm.data import adapter
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


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
        
        self._channelMock.stderr = "ANS1083E No files have..."
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
