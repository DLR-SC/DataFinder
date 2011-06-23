# pylint: disable=W0511
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
Tests the data adapter implementation.
"""


import io
import unittest

from datafinder.persistence.adapters.svn.data import adapter as svn_adapter
from datafinder.persistence.adapters.svn.error import SubversionError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock 


__version__ = "$Revision-Id$" 



class _OsModuleMock(SimpleMock):
    """ Mocks the relevant functions of the os module. """
    
    def __init__(self, pathMock, returnValue=None, error=None):
        """ Constructor. """
        
        SimpleMock.__init__(self, returnValue, error)
        self.returnValue = returnValue
        self.error = error
        self.path = pathMock
        
    @staticmethod
    def strerror(errorNumber):
        """ Explicitly mocking the error code function. """
        
        return str(errorNumber)


class _OpenMock(object):
    """ Mocks the built-in open function. """
    
    def __init__(self):
        """ Constructor. """
        
        self.error = False
        
    def __call__(self, *_, **__):
        """ Emulates the call to the open function. """
        
        if self.error:
            raise IOError("")
        else:
            return io.StringIO("")

    
class DataSubversionAdapterTestCase(unittest.TestCase):
    """ Tests the SVN - data adapter implementation. """
    
    def setUp(self):
        # Install os mock
        self._osPathMock = SimpleMock()
        self._osModuleMock = _OsModuleMock(self._osPathMock)
        svn_adapter.os = self._osModuleMock
        # Install shutil mock
        self._shutilMock = SimpleMock()
        svn_adapter.shutil = self._shutilMock
        # Install open mock
        self._openMock = _OpenMock()
        self._openFunction = globals()["__builtins__"]["open"]
        globals()["__builtins__"]["open"] = self._openMock
        
        self._connectionMock = SimpleMock(workingCopyPath="")
        self._adapter = svn_adapter.DataSubversionAdapter(
            "/path/identify", SimpleMock(self._connectionMock))
        
    def tearDown(self):
        globals()["__builtins__"]["open"] = self._openFunction
           
    def testLinkTarget(self):
        # Is a link
        self._connectionMock.methodNameResultMap = \
            {"getProperty": ("/thelinkTargetPath", None)}
        self.assertEquals(self._adapter.linkTarget, "/thelinkTargetPath")
        self.assertTrue(self._adapter.isLink)

        # No link
        self._connectionMock.methodNameResultMap = None
        self._connectionMock.error = SubversionError("")
        self.assertEquals(self._adapter.linkTarget, None)
        self.assertFalse(self._adapter.isLink)
                
    def testIsLeaf(self):
        # Success
        self._connectionMock.value = True
        self.assertTrue(self._adapter.isLeaf)
        
        self._connectionMock.value = False
        self.assertFalse(self._adapter.isLeaf)
        
        # Error
        self._connectionMock.error = SubversionError("")
        try:
            isLeaf = self._adapter.isLeaf
            self.fail("No PersistenceError. Get '%s' instead." % str(isLeaf))
        except PersistenceError:
            self.assertTrue(True)
            
    def testIsCollection(self):
        # Success
        self._connectionMock.value = True
        self.assertTrue(self._adapter.isCollection)
        self.assertTrue(self._adapter.canAddChildren)
        
        self._connectionMock.value = False
        self.assertFalse(self._adapter.isCollection)
        self.assertFalse(self._adapter.canAddChildren)

        # Error
        self._connectionMock.error = SubversionError("")
        try:
            isCollection = self._adapter.isCollection
            self.fail("No PersistenceError. Get '%s' instead." % str(isCollection))
        except PersistenceError:
            self.assertTrue(True)

    def testCreateResource(self):
        # Success
        self._adapter.createResource()
        # Local not versioned directory exists but gets removed
        self._osPathMock.methodNameResultMap = {"exists": (True, None), "isdir": (True, None)}
        self._adapter.createResource()
        
        # Error
        # Problem to commit resource
        self._connectionMock.error = SubversionError("")
        self.assertRaises(PersistenceError, self._adapter.createResource)
        
        # Local file cannot be created
        self._connectionMock.error = None
        self._openMock.error = True
        self.assertRaises(PersistenceError, self._adapter.createResource)
        
        # Local directory cannot be removed
        self._osPathMock.methodNameResultMap = {"exists": (True, None), "isdir": (True, None)}
        self._shutilMock.error = OSError("")
        self.assertRaises(PersistenceError, self._adapter.createResource)
    
    def testCreateCollection(self):
        # Success
        self._adapter.createCollection()
        self._osPathMock.value = True
        self._adapter.createCollection(True)
        # Local not versioned file exists but gets removed
        self._osPathMock.methodNameResultMap = {"exists": (True, None), "isdir": (False, None)}
        self._adapter.createCollection()
        
        # Error
        # Problem to commit directory
        self._connectionMock.error = SubversionError("")
        self.assertRaises(PersistenceError, self._adapter.createCollection)
        
        # Problem creating local directory
        self._connectionMock.error = None
        self._osModuleMock.error = OSError("")
        self.assertRaises(PersistenceError, self._adapter.createCollection)
        
        # Local directory cannot be removed
        self._osPathMock.methodNameResultMap = {"exists": (True, None), "isdir": (False, None)}
        self.assertRaises(PersistenceError, self._adapter.createCollection)
    
    def testCreateLink(self):
        # Success
        self._adapter.createLink(SimpleMock(identifier="/destPath"))
        
        # Error
        self._connectionMock.methodNameResultMap = \
            {"setProperty": (None, SubversionError(""))}
        self.assertRaises(PersistenceError, self._adapter.createLink, 
                          SimpleMock(identifier="/destPath"))
    
    def testGetChildren(self):
        # Success
        self._connectionMock.value = ["/trunk/test/test.txt"]
        self.assertEquals(self._adapter.getChildren(), ["/trunk/test/test.txt"])
    
        # Error
        self._connectionMock.error = SubversionError("")
        self.assertRaises(PersistenceError, self._adapter.getChildren)
        
    def testWriteData(self):
        # Success
        self._adapter.writeData(io.StringIO("test"))
        
        # Error
        self._openMock.error = True
        self.assertRaises(PersistenceError, self._adapter.writeData, io.StringIO(""))
        self._connectionMock.error = SubversionError("")
        self.assertRaises(PersistenceError, self._adapter.writeData, io.StringIO(""))
        
    def testReadData (self):
        # Success
        self._adapter.readData()
        
        # Error
        self._openMock.error = True
        self.assertRaises(PersistenceError, self._adapter.readData)
        self._connectionMock.error = SubversionError("")
        self.assertRaises(PersistenceError, self._adapter.readData)
        
    def testDelete (self):
        # Success
        self._adapter.delete()

        # Error
        self._connectionMock.error = SubversionError("")
        self.assertRaises(PersistenceError, self._adapter.delete)

    def testMove(self):
        destination = SimpleMock(identifier="/")
        
        # Success
        self._adapter.move(destination)
        
        # Error
        self._connectionMock.error = SubversionError("")
        self.assertRaises(PersistenceError, self._adapter.move, destination)
        
    def testCopy(self):
        destination = SimpleMock(identifier="/")
        
        # Success
        self._adapter.copy(destination)
        
        # Error
        self._connectionMock.error = SubversionError("")
        self.assertRaises(PersistenceError, self._adapter.copy, destination)
        
    def testExists(self):
        # Success
        self.assertTrue(self._adapter.exists()) 
        self._connectionMock.error = SubversionError("")
        self.assertFalse(self._adapter.exists())
