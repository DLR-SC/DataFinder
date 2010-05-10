# pylint: disable-msg=R0201
# R0201 is disabled to provide a correct mock implementation.
# Usage of the @staticmehtod decorator is not possible.
#
# Created: 21.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: factory_test.py 4626 2010-04-20 20:57:02Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements test cases for the file system factory.
"""


import re
import unittest

from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import FileSystem
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4626 $"


_UNSUPPORTED_URI_SCHEME = "unknown"
_VALID_URI_SCHEME = "valid"
_VALID_PRINCIPAL_SEARCH_SCHEME = "valid_principal"


class _ConcreteFactoryMock(BaseFileSystem):
    """ Mocks the concrete factory implementation. """
    
    def __init__(self, _):
        """ Constructor. """
        
        BaseFileSystem.__init__(self)
    
    def createDataStorer(self, _):
        """ Mock implementation. """
        
        mock = SimpleMock(True)
        mock.identifier = "id"
        return mock
    
    def createMetadataStorer(self, _):
        """ Mock implementation. """
        
        mock = SimpleMock()
        mock.identifier = "id"
        return mock
    
    def createPrincipalSearcher(self):
        """ Mock implementation. """
        
        class PrincipalSearcherMock(object):
            def searchPrincipal(self, _, __):
                return [""]
        return PrincipalSearcherMock()
    
    def createPrivilegeStorer(self, _):
        """ Mock implementation. """
        
        mock = SimpleMock()
        mock.identifier = "id"
        return mock
    
    @property
    def hasCustomMetadataSupport(self):
        """ Mock implementation. """
        
        return True
    
    @property
    def hasMetadataSearchSupport(self):
        """ Mock implementation. """
        
        return True
    
    @property
    def hasPrivilegeSupport(self):
        """ Mock implementation. """
        
        return True
    
    @property
    def metadataIdentifierPattern(self):
        """ Mock implementation. """
        
        return re.compile(".")
    
    @property
    def identifierPattern(self):
        """ Mock implementation. """
        
        return re.compile(".")


class _ConcretePrincipalSeacherFactoryMock(BaseFileSystem):
    """ Mocks the concrete factory implementation. """
    
    def __init__(self, _):
        """ Constructor. """
        
        BaseFileSystem.__init__(self)
    
    def createPrincipalSearcher(self):
        """ Mock implementation. """
        
        class PrincipalSearcherMock(object):
            def searchPrincipal(self, _, __):
                return ["", ""]
        return PrincipalSearcherMock()


def _getFactoryMock(_, uriScheme):
    """ Raises a persistence error. """
    
    if uriScheme == _UNSUPPORTED_URI_SCHEME:
        raise PersistenceError("")
    elif uriScheme == _VALID_PRINCIPAL_SEARCH_SCHEME:
        return _ConcretePrincipalSeacherFactoryMock
    else:
        return _ConcreteFactoryMock


class FileSystemTestCase(unittest.TestCase):
    """ Test cases for the file system factory. """
    
    def setUp(self):
        """ Mocks the factory creation method. """
        
        FileSystem._getFactory = _getFactoryMock
            
    def testNullFactory(self):
        """ Checks the initialization of a null factory. """
        
        nullFileSystem = FileSystem()
        self.assertEquals(nullFileSystem.searchPrincipal("pattern", "searchMode"), list())
        self.assertTrue(not nullFileSystem.createFileStorer("identifier") is None)
        self.assertFalse(nullFileSystem.hasCustomMetadataSupport)
        self.assertFalse(nullFileSystem.hasMetadataSearchSupport)
        self.assertFalse(nullFileSystem.hasPrivilegeSupport)
        self.assertEquals(nullFileSystem.isValidIdentifier(""), (True, None))
        self.assertEquals(nullFileSystem.isValidMetadataIdentifier(""), (True, None))
        self.assertEquals(nullFileSystem.baseUri, None)
        self.assertEquals(nullFileSystem.baseConfiguration, None)
        self.assertEquals(nullFileSystem.isAccessible, False)
        nullFileSystem.updateCredentials(dict())
        nullFileSystem.updatePrincipalSearchCredentials(dict())
        nullFileSystem.release()

    def testInvalidInterfaceType(self):
        """ Tests the behavior when an unsupported interface type is provided. """
        
        baseConf = SimpleMock()
        baseConf.uriScheme = _UNSUPPORTED_URI_SCHEME
        self.assertRaises(PersistenceError, FileSystem, baseConf)
    
    def testValidInterfaceType(self):
        """ Tests the behavior when a valid interface type is provided. """
        
        baseConf = SimpleMock()
        baseConf.uriScheme = _VALID_URI_SCHEME
        fileSystem = FileSystem(baseConf)
        self.assertTrue(fileSystem.searchPrincipal("pattern", "searchMode"), 1)
        fileStorer = fileSystem.createFileStorer("identifier")
        self.assertFalse(fileStorer is None)
        self.assertFalse(fileStorer.dataStorer is None)
        self.assertFalse(fileStorer.metadataStorer is None)
        self.assertFalse(fileStorer.privilegeStorer is None)
        self.assertTrue(fileSystem.hasCustomMetadataSupport)
        self.assertTrue(fileSystem.hasMetadataSearchSupport)
        self.assertTrue(fileSystem.hasPrivilegeSupport)
        self.assertEquals(fileSystem.isValidIdentifier(""), (True, None))
        self.assertEquals(fileSystem.isValidMetadataIdentifier(""), (True, None))
        self.assertNotEquals(fileSystem.baseUri, None)
        self.assertNotEquals(fileSystem.baseConfiguration, None)
        self.assertEquals(fileSystem.isAccessible, True)
        fileSystem.updateCredentials(dict())
        fileSystem.updatePrincipalSearchCredentials(dict())
        fileSystem.release()
        
    def testDifferentPrincipalSearchInterface(self):
        """ Tests the combination of a file system interface with another one for principal search. """
        
        baseConf = SimpleMock()
        baseConf.uriScheme = _VALID_URI_SCHEME
        principalSearchBaseConf = SimpleMock()
        principalSearchBaseConf.uriScheme = _VALID_PRINCIPAL_SEARCH_SCHEME
        fileSystem = FileSystem(baseConf, principalSearchBaseConf)
        self.assertTrue(fileSystem.searchPrincipal("pattern", "searchMode"), 2)
