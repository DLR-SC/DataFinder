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
Implements the principal search WebDAV-specific 
"""


import os

from webdav.Condition import ContainsTerm
from webdav.Connection import WebdavError
from webdav.Constants import NS_DAV, PROP_DISPLAY_NAME

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.principal_search import constants, principal
from datafinder.persistence.principal_search.principalsearcher import NullPrincipalSearcher
from datafinder.persistence.adapters.webdav_ import util


__version__ = "$Revision-Id:$" 


class PrincipalSearchWebdavAdapter(NullPrincipalSearcher):
    """ Implements the search for principals WebDAV-specific. """
    
    def __init__(self, userCollectionUrl, groupCollectionUrl, connectionPool, connectionHelper=util):
        """
        Constructor.
        
        @param userCollectionUrl: URL pointing to the user collection.
        @type userCollectionUrl: C{unicode}
        @param groupCollectionUrl: URL pointing to the group collection.
        @type groupCollectionUrl: C{unicode}
        @param connectionPool: Connection pool.
        @type connectionPool: L{Connection<datafinder.persistence.webdav_.connection_pool.WebdavConnectionPool>}
        @param connectionHelper: Utility object/module creating WebDAV library storer instances.
        @type connectionHelper: L{ItemIdentifierMapper<datafinder.persistence.adapters.webdav_.util}
        """
        
        NullPrincipalSearcher.__init__(self)
        self.__connectionPool = connectionPool
        self.__userCollectionUrl = userCollectionUrl
        self.__groupCollectionUrl = groupCollectionUrl
        self.__connectionHelper = connectionHelper
    
    def searchPrincipal(self, pattern, searchMode):
        """ @see: L{NullPrincipalSearcher<datafinder.persistence.principal_search.principalsearcher.NullPrincipalSearcher>} """
        
        connection = self.__connectionPool.acquire()
        try:
            userCollectionStorer = self.__connectionHelper.createCollectionStorer(self.__userCollectionUrl, connection)
            groupCollectionStorer = self.__connectionHelper.createCollectionStorer(self.__groupCollectionUrl, connection)
            return self._searchPrincipal(pattern, searchMode, userCollectionStorer, groupCollectionStorer)
        finally:
            self.__connectionPool.release(connection)

    def _searchPrincipal(self, pattern, searchMode, userCollectionStorer, groupCollectionStorer):
        """ Performs principal search on the WebDAV server. """
            
        mappedResult = list()
        userRawResult = dict()
        groupRawResult = dict()
        if searchMode == constants.SEARCH_MODE_USER_AND_GROUP:
            groupRawResult = self._performSearch(pattern, groupCollectionStorer)
            userRawResult = self._performSearch(pattern, userCollectionStorer)
        elif searchMode == constants.SEARCH_MODE_GROUP_ONLY:
            groupRawResult = self._performSearch(pattern, groupCollectionStorer)
        elif searchMode == constants.SEARCH_MODE_USER_ONLY:
            userRawResult = self._performSearch(pattern, userCollectionStorer)
        else:
            raise PersistenceError("The specified search mode is not supported.")
        self._mapRawResult(userRawResult, mappedResult, True)
        self._mapRawResult(groupRawResult, mappedResult, False)
        return mappedResult

    @staticmethod
    def _performSearch(name, collectionStorer):
        """ Performs the principal search on the given WebDAV principal collection. """
        
        condition = ContainsTerm(PROP_DISPLAY_NAME, name, False)
        try:
            searchResult = collectionStorer.search(condition, [(NS_DAV, PROP_DISPLAY_NAME)])
        except WebdavError, error:
            errorMessage = "Cannot perform user/group query. Reason: %s" % error.reason
            raise PersistenceError(errorMessage)
        return searchResult

    @staticmethod
    def _mapRawResult(rawResult, mappedResult, isUser):
        """ Maps the WebDAV search result to the required format. """
        
        for key, value in rawResult.iteritems():
            uniqueName = os.path.basename(key)
            displayName = ""
            if (NS_DAV, PROP_DISPLAY_NAME) in value:
                displayName = unicode(value[(NS_DAV, PROP_DISPLAY_NAME)].textof())
            if isUser:
                principalType = constants.USER_PRINCIPAL_TYPE
            else:
                principalType = constants.GROUP_PRINCIPAL_TYPE
            principal_ = principal.Principal(uniqueName, type=principalType, displayName=displayName)
            mappedResult.append(principal_)
