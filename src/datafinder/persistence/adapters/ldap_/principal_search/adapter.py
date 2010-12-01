# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#
#met:
#
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


""" Adapts the principal search interface to the LDAP protocol. """


import ldap

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.principal_search import constants, principal
from datafinder.persistence.principal_search.principalsearcher import NullPrincipalSearcher


__version__ = "$Revision-Id:$" 


_LDAP_PROPERTY_OBJECT_CLASS = "objectClass"
_LDAP_PROPERTY_COMMON_NAME = "cn"
_LDAP_PROPERTY_DISPLAY_NAME = "displayName"
_LDAP_PROPERTY_OBJECT_CLASS_USER_VALUE = "user"
_LDAP_PROPERTY_OBJECT_CLASS_GROUP_VALUE = "group"
_LDAP_PROPERTY_MEMBEROF_NAME = "memberOf"
_LDAP_WILDCARD_CHARACTER = "*"
_DOMAIN_SEPARATOR = "\\"

_FILTER = {_LDAP_PROPERTY_COMMON_NAME: 0,
           _LDAP_PROPERTY_OBJECT_CLASS: 1,
           _LDAP_PROPERTY_DISPLAY_NAME: 2,
           _LDAP_PROPERTY_MEMBEROF_NAME: 3}

_userQuery = "(&%s (%s=%s))" % ("(%s=" + _LDAP_PROPERTY_DISPLAY_NAME + ")",
                                _LDAP_PROPERTY_OBJECT_CLASS,
                                _LDAP_PROPERTY_OBJECT_CLASS_USER_VALUE)
_groupQuery = "(&%s (%s=%s))" % ("(%s=" + _LDAP_PROPERTY_COMMON_NAME + ")",
                                 _LDAP_PROPERTY_OBJECT_CLASS,
                                 _LDAP_PROPERTY_OBJECT_CLASS_GROUP_VALUE)


class LdapPrincipalSearchAdapter(NullPrincipalSearcher):
    """ LDAP-specific implementation of the principal search. """
    
    def __init__(self, configuration):
        """ 
        Constructor. 
        
        @param configuration: LDAP-specific configuration parameters.
        @type configuration: L{Configuration<datafinder.persistence.ldap.configuration.Configuration>}
        """
        
        NullPrincipalSearcher.__init__(self)
        self._configuration = configuration
    
    def searchPrincipal(self, pattern, searchMode):
        """ @see: L{NullPrincipalSearcher<datafinder.persistence.principal_search.principalsearcher.NullPrincipalSearcher>} """
        
        connection = self._createConnection()
        try:
            pattern = _LDAP_WILDCARD_CHARACTER + pattern + _LDAP_WILDCARD_CHARACTER
            userQuery = _userQuery % pattern
            groupQuery = _groupQuery % pattern
            rawResult = list()
            try:
                if searchMode == constants.SEARCH_MODE_USER_AND_GROUP:
                    rawResult = list()
                    rawResult.extend(connection.search(userQuery, self._configuration.baseDn, filterDictionary=_FILTER))
                    rawResult.extend(connection.search(groupQuery, self._configuration.baseDn, filterDictionary=_FILTER))
                elif searchMode == constants.SEARCH_MODE_USER_ONLY:
                    rawResult = connection.search(userQuery, self._configuration.baseDn, filterDictionary=_FILTER)
                elif searchMode == constants.SEARCH_MODE_GROUP_ONLY:
                    rawResult = connection.search(groupQuery, self._configuration.baseDn, filterDictionary=_FILTER)
                else:
                    raise PersistenceError("Search mode '%s' is not supported." % searchMode)
            except ldap.LDAPError, error:
                errorMessage = "Problems on querying the LDAP server occurred. Problem: '%s'" % str(error)
                raise PersistenceError(errorMessage)
            else:
                return self._mapRawResult(rawResult)
        finally:
            connection.close()
    
    def _createConnection(self):
        """ Creates a connection accessing the specified LDAP server. """
        
        try:
            connection = _Ldap(self._configuration.serverUri, self._configuration.username, 
                               self._configuration.password, encoding=self._configuration.encoding)
        except ldap.LDAPError, error:
            errorMessage = "Cannot perform principal search on LDAP server. Reason: '%s'" % str(error)
            raise PersistenceError(errorMessage)
        else:
            return connection
        
    def _mapRawResult(self, rawResult):
        """ Prepare LDAP query result. """
        
        mappedResult = list()
        for item in rawResult:
            uniqueName = self._configuration.domain + _DOMAIN_SEPARATOR + unicode(item[0][0], self._configuration.encoding)
            displayName = ""
            if not item[2][0] is None:
                displayName = unicode(item[2][0], self._configuration.encoding)
            if _LDAP_PROPERTY_OBJECT_CLASS_USER_VALUE in item[1]:
                principalType = constants.USER_PRINCIPAL_TYPE
            else:
                principalType = constants.GROUP_PRINCIPAL_TYPE
            memberOf = list()
            if not item[3] is None:
                for member in item[3]:
                    uniqueMemberName = self._configuration.domain + _DOMAIN_SEPARATOR + unicode(member, self._configuration.encoding)
                    member = principal.Principal(uniqueMemberName, type=constants.GROUP_PRINCIPAL_TYPE)
                    memberOf.append(member)
            principal_ = principal.Principal(uniqueName, type=principalType, displayName=displayName, roles=memberOf)
            mappedResult.append(principal_)
        return mappedResult


class _Ldap(object):
    """
    This class provides functionality for handling LDAP queries.
    
    @version: $Revision$
    @author:  Guy K. Kloss
    @contact: U{guy.kloss@dlr.de}
    
    @ivar handle: Handle to LDAP server connection.
    @type handle: L{ldap.ldapobject.SimpleLDAPObject}
    """
    
    def __init__(self, ldapServerUri=None, userDN="", password="", encoding="UTF-8", ldapVersion=ldap.VERSION3):
        """
        Constructor is to be called with applying connection parameters 
        to bind to LDAP server. The call should preferrably be handled 
        by specifying key-value pairs according to method's signature.
        
        @param ldapServerUri: Alternative to host+port setting, in an URI 
                              as described in RFC 2255 (default: None).
        @type ldapServerUri: C{string}
        @param userDN: User to connect to LDAP server. L{baseDN} is appended 
                       automatically for connection (default: "").
        @type userDN: C{string}
        @param password: Password for L{userDN} to connect (default: "").
        @type password: C{string}
        @param ldapVersion: LDAP protocol version to speak for LDAP connect.
        @type ldapVersion: C{int}
        
        @raise LdapError: L{Ldap.LdapError} is raised on a failed connect.
        """
    
        self._handle = None
        self._encoding = encoding
        self._handle = ldap.initialize(ldapServerUri)
        self._handle.protocol_version = ldapVersion
        self._handle.simple_bind_s(userDN, password)
      
    def search(self, query, baseDN, scope=ldap.SCOPE_SUBTREE, \
               timeout=0, filterDictionary=None):
        """
        Searches the LDAP server with the given query. For further reference 
        on the parameters and options see Python LDAP module documentation.
        
        Returned result sets from the plain LDAP query are constructed the 
        following way:
            
            List              # list of entries
              List            # list of elements within entry (observed to be always === 1)
                Tuple         # the entry itself
                  String      # CN (full descriptor of entry like FQDN/URL)
                  Dictionary  # attributes as key/value pairs
        
        If a filter is present, result sets get simplified and are constructed this way::
            
            List              # list of entries
              Dictionary      # The entry itself with attributes as key/value pairs.
                              # The value is a PyList of entries.

        @param query: Query string to "ask" the LDAP server for.
        @type query: C{string}
        @param baseDN: Search base to start search from (CN).
        @type baseDN: C{string}
        @param scope: Scope of search depth within tree 
                      (default: ldap.SCOPE_SUBTREE).
        @type scope: See Python LDAP module documentation.
        @param timeout: Timeout for LDAP search query (default: 0).
        @type timeout: See Python LDAP module documentation.
        @param filterDictionary: Mapping of LDAP attributes to desired target names. All 
                                 attributes the filter contains will be present in returned result set.
                                 To omit certain attributes, just leave them out. In other words: add all 
                                 desired attributes with the desired mapping name to the filter 
                                (default: None).
        @type filterDictionary: C{dict} (See documentation of L{_filterResults} 
                                for further details.)
        
        @return: List of results that match the query.
        @rtype: C{list} of complex sequence types returned by query.
                See above for further information on structure. If a filter is 
                set, a list of C{dict} (one for each result item) is 
                returned with the filter mapping of attributes. See documentation 
                of L{_filterResults} for further details.
        
        @raise ldap.LDAPError indicating problems on LDAP search.
        """
        
        if not self._handle:
            raise ldap.LDAPError("The LDAP connection has not been initialized.")
        resultSet = list()
        self._handle.set_option(ldap.OPT_REFERRALS, 0)
        resultId = self._handle.search(baseDN, 
                                       scope, 
                                       query.encode(self._encoding), 
                                       None)
        while True:
            resultType, resultData = self._handle.result(resultId, timeout)
            if (len(resultData) == 0):
                break
            else:
                if resultType == ldap.RES_SEARCH_ENTRY:
                    resultSet.append(resultData)
        if not filterDictionary is None:
            resultSet = self._filterResults(resultSet, filterDictionary)
        return resultSet
    
    @staticmethod
    def _filterResults(results, filterDictionary):
        """
        Filters retrieved results and gives them a form that is much nicer to use 
        later on in other modules. The filter contains the attributes of the entries 
        that are wanted in the result set. It also maps the attribute names from the 
        LDAP query to names that are desired in the result set returned.
        
        @param results: Result set returned by LDAP search query.
        @type results: C{list} of complex sequence types returned by query.
                       @see L{LDAP.search} for further information on structure.
        @param filterDictionary: Mapping of LDAP attributes to desired target names. All 
                                 attributes the filter contains will be present in returned result set.
                                 To omit certain attributes, just leave them out. In other words: add all 
                                 desired attributes with the desired mapping name to the filter.
        @type filterDictionary: C{dict}
        
        @return: Filtered set of results.
        @rtype: C{list} of C{dict}
        """
        
        if len(results) == 0 or len(filterDictionary) == 0:
            return list()
        filteredResults = list()
        # go through all results
        for result in results:
            filterResult = dict()
            # go through all entries of the result ... (should be usually just one in our case)
            for entry in result:
                filteredEntry = dict()
                # ... and extract all fields from filterDictionary
                for item in filterDictionary:
                    value = entry[1].get(item, [None])
                    filteredEntry = {filterDictionary[item]: value}
                    filterResult.update(filteredEntry)
            filteredResults.append(filterResult)
        return filteredResults

    def close(self):
        """ Closes the LDAP connection. """
        
        try:
            self._handle.unbind()
        except ldap.LDAPError: # Ignoring error
            self._handle = None
        finally:
            self._handle = None
