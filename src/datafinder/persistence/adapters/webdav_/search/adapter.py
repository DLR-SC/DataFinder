## $Filename$ 
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


""" Adapts the search interface to the WebDAV library. """


from webdav import Constants
from webdav.Connection import WebdavError

from datafinder.persistence.adapters.webdav_ import util
from datafinder.persistence.adapters.webdav_.search.search_restriction_mapping import mapSearchRestriction
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.search.searcher import NullSearcher


__version__ = "$Revision-Id:$" 


class SearchWebdavAdapter(NullSearcher):
    """ WebDAV-specific implementation of the search. """
    
    def __init__(self, connectionPool, itemIdMapper, connectionHelper=util):
        """ 
        Constructor. 
        
        @param connectionPool: Connection pool.
        @type connectionPool: L{Connection<datafinder.persistence.webdav_.connection_pool.WebdavConnectionPool>}
        @param itemIdMapper: Utility object mapping item identifiers. 
        @type itemIdMapper: L{ItemIdentifierMapper<datafinder.persistence.adapters.webdav_.util.ItemIdentifierMapper}
        @param connectionHelper: Utility object/module creating WebDAV library storer instances.
        @type connectionHelper: L{ItemIdentifierMapper<datafinder.persistence.adapters.webdav_.util}
        """
 
        NullSearcher.__init__(self)
        self.__connectionPool = connectionPool
        self.__itemIdMapper = itemIdMapper
        self.__connectionHelper = connectionHelper

    def search(self, restrictions, destination):
        """ @see: L{NullPrincipalSearcher<datafinder.persistence.search.searcher.NullSearcher>} """
        
        result = list()
        connection = self.__connectionPool.acquire()
        try:
            try:
                restrictions = mapSearchRestriction(restrictions)
            except AssertionError:
                restrictions = list()
            persistenceId = self.__itemIdMapper.mapIdentifier(destination.identifier)
            collectionStorer = self.__connectionHelper.createCollectionStorer(persistenceId, connection)
            try:
                rawResult = collectionStorer.search(restrictions, [Constants.PROP_DISPLAY_NAME])
            except WebdavError, error:
                errorMessage = "Problem during meta data search." \
                                + "Reason: '%s'" % error.reason 
                raise PersistenceError(errorMessage)
            else:
                for persistenceId in rawResult.keys():
                    result.append(self.__itemIdMapper.mapPersistenceIdentifier(persistenceId))
        finally:
            self.__connectionPool.release(connection)
        return result
