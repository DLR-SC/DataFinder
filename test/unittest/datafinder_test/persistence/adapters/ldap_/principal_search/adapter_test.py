# pylint: disable-msg=W0613
# W0613 - "unused arguments" The mock has to provide the same interface but at
#         the moment it is not necessary to evaluate all parameters.
#
#
# Created: Tobias Schlauch (Tobias.Schlauch@dlr.de)
#
# Version: $Id: adapter_test.py 3880 2009-03-25 17:22:09Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


""" Test cases for the LDAP-specific principal search adapter. """


import ldap
import unittest

from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.principal_search import constants, principal
from datafinder.persistence.adapters.ldap_.configuration import Configuration
from datafinder.persistence.adapters.ldap_.principal_search import adapter


__version__ = "$LastChangedRevision: 3880 $"


_TEST_DOMAIN = "dlr"
_SERVER_DOWN_URI = "uriDown"

_VALID_USER_QUERY = "validUser"
_VALID_GROUP_QUERY = "validGroup"
_VALID_USER_GROUP_QUERY = "validUserGroup"
_INVALID_QUERY = "invalidQuery"
_PROBLEM_ON_QUERY = "problemOnQuery"

_GROUP1_PRINCIPAL = principal.Principal(_TEST_DOMAIN + "\\group1", type=constants.GROUP_PRINCIPAL_TYPE)
_GROUP2_PRINCIPAL = principal.Principal(_TEST_DOMAIN + "\\group2", type=constants.GROUP_PRINCIPAL_TYPE)
_ROLES = [_GROUP1_PRINCIPAL, _GROUP2_PRINCIPAL]

_RAW_USER_RESULT = [{0: ["test"], 1: ["user"], 2: ["test"], 3: ["group1", "group2"]}]
_MAPPED_USER = principal.Principal(_TEST_DOMAIN + "\\test", displayName="test", roles=_ROLES) 

_RAW_GROUP_RESULT = [{0: ["test1"], 1: ["group"], 2: ["test"], 3: ["group1", "group2"]}]
_MAPPED_GROUP = principal.Principal(_TEST_DOMAIN + "\\test1", type=constants.GROUP_PRINCIPAL_TYPE, displayName="test", roles=_ROLES)


class _LdapConnectionMock(object):
    """ Class to mock class C{_Ldap}. """

    def __init__(self, ldapServerUri, _, __, encoding=None):
        """
        Constructor. 
        """
        
        self.__searchCalls = 0
        self.searchStateDictionary = {_VALID_USER_QUERY: self._returnValidUserResult,
                                      _VALID_GROUP_QUERY: self._returnValidGroupResult,
                                      _INVALID_QUERY: self._raiseLdapError,
                                      _PROBLEM_ON_QUERY: self._raiseLdapError}
        if ldapServerUri == _SERVER_DOWN_URI:
            self._raiseLdapError()
        
    def search(self, query, _, filterDictionary=None):
        """ Mocked search method. """
        
        if _VALID_USER_GROUP_QUERY in query:
            if self.__searchCalls == 0:
                self.__searchCalls += 1
                return _RAW_USER_RESULT 
            else:
                return _RAW_GROUP_RESULT
        else:
            state = None
            for key in self.searchStateDictionary:
                if key in query:
                    state = key
                    break
            return self.searchStateDictionary[state]()
        
    def close(self):
        """ Mocked close method. """
    
        pass

    @staticmethod
    def _raiseLdapError():
        """ Raises a LdapInvalidQueryError. """
        
        raise ldap.LDAPError("Error!")
    
    @staticmethod
    def _returnValidUserResult():
        """ Returns valid user search result. """
        
        return _RAW_USER_RESULT
    
    @staticmethod
    def _returnValidGroupResult():
        """ Returns valid group search result. """
        
        return _RAW_GROUP_RESULT


class LdapSearchTestCase(unittest.TestCase):
    """ Test cases for function that return the LDAP connection. """
    
    def setUp(self):
        """ Enables mock connection. """
        
        adapter._Ldap = _LdapConnectionMock
        self._configuration = Configuration(BaseConfiguration())
        self._configuration.domain = _TEST_DOMAIN
        self._ldapPrincipalSearcher = adapter.LdapPrincipalSearchAdapter(self._configuration)
        
    def testValidUserResult(self):
        """ Tests the successful search for a specific user. """
        
        result = self._ldapPrincipalSearcher.searchPrincipal(_VALID_USER_QUERY, constants.SEARCH_MODE_USER_ONLY)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0], _MAPPED_USER)

    def testValidGroupResult(self):
        """ Tests the successful search for a specific group. """
        
        result = self._ldapPrincipalSearcher.searchPrincipal(_VALID_GROUP_QUERY, constants.SEARCH_MODE_GROUP_ONLY)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0], _MAPPED_GROUP)

    def testValidUserGroupResult(self):
        """ Tests the successful search for a specific user and group. """
        
        result = self._ldapPrincipalSearcher.searchPrincipal(_VALID_USER_GROUP_QUERY, constants.SEARCH_MODE_USER_AND_GROUP)
        self.assertEquals(len(result), 2)
        self.assertEquals(result[0], _MAPPED_USER)
        self.assertEquals(result[1], _MAPPED_GROUP)

    def testIvalidSearchMode(self):
        """ Tests behavior in case of an invalid search mode. """
        
        self.assertRaises(PersistenceError, self._ldapPrincipalSearcher.searchPrincipal,
                          _VALID_USER_GROUP_QUERY, "invalidSearchMode")
    
    def testInvalidConnectionParameters(self):
        """ Tests the behavior when invalid connection parameters are provided. """
        
        self._configuration.serverUri = _SERVER_DOWN_URI
        self.assertRaises(PersistenceError, self._ldapPrincipalSearcher.searchPrincipal,
                          _VALID_USER_GROUP_QUERY, constants.SEARCH_MODE_GROUP_ONLY)
    
    def testProblemOnPerformingQuery(self):
        """ Tests the behavior when a problem during performance of the query occurs. """
        
        self.assertRaises(PersistenceError, self._ldapPrincipalSearcher.searchPrincipal,
                          _PROBLEM_ON_QUERY, constants.SEARCH_MODE_GROUP_ONLY)
