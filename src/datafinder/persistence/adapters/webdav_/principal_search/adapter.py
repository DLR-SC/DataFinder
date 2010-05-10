#
# Created: 12.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: adapter.py 3805 2009-02-23 13:00:19Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


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


__version__ = "$LastChangedRevision: 3805 $"


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
