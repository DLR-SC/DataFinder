#
# Created: 05.03.2010 Patrick Schaefer <patrick.schaefer@dlr.de>
#
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


"""
Test case for the repository module.
"""


import unittest

from datafinder.core.error import ConfigurationError
from datafinder.script_api import repository
from datafinder.script_api.error import ScriptApiError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4542 $"


class RepositoryTestCase(unittest.TestCase):
    """
    The TestCase for the repository module.
    """
    
    def setUp(self):
        """
        Creates the required mocks.
        """
        
        self._disconnectRepositoryMock = SimpleMock()
        self._repositoryMock = SimpleMock()
        self._connectRepositoryMock = SimpleMock(self._repositoryMock)
        self._repositoryManagerInstanceMock = SimpleMock(self._disconnectRepositoryMock)
        repository.repositoryManagerInstance = self._repositoryManagerInstanceMock
        repository.RepositoryDescription = self._repositoryMock
        

    def testConnectRepository(self):
        """
        Test for the connectRepository method.
        """
        
        self._repositoryMock.error = ConfigurationError("")
        
        self.assertRaises(ScriptApiError, repository.connectRepository, "", "", "", "")
    
    
    def testDisconnectRepository(self):
        """
        Test for the disconnectRepository method.
        """
        
        self._repositoryManagerInstanceMock.error = ConfigurationError("")
        
        self.assertRaises(ScriptApiError, repository.disconnectRepository, repository.RepositoryDescription)
    
        