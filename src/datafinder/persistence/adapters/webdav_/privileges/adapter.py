#
# Created: 29.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: adapter.py 3805 2009-02-23 13:00:19Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the privilege adapter.
"""


from webdav.Connection import WebdavError

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.privileges.privilegestorer import NullPrivilegeStorer
from datafinder.persistence.adapters.webdav_ import util


__version__ = "$LastChangedRevision: 3805 $"


class PrivilegeWebdavAdapter(NullPrivilegeStorer):
    """ Privilege adapter implementation. """
    
    def __init__(self, identifier, connectionPool, itemIdMapper, privilegeMapper, connectionHelper=util):
        """
        Constructor.
        
        @param identifier: Logical identifier of the resource.
        @type identifier: C{unicode}
        @param connectionPool: Connection pool.
        @type connectionPool: L{Connection<datafinder.persistence.webdav_.connection_pool.WebdavConnectionPool>}
        @param itemIdMapper: Utility object mapping item identifiers. 
        @type itemIdMapper: L{ItemIdentifierMapper<datafinder.persistence.adapters.webdav_.util.ItemIdentifierMapper}
        @param privilegeMapper: Utility object mapping ACLs and prvileges.
        @type privilegeMapper: L{PrivilegeMapper<datafinder.persistence.adapters.webdav_.privileges.privileges_mapping.PrivilegeMapper>} 
        @param connectionHelper: Utility object/module creating WebDAV library storer instances.
        @type connectionHelper: L{ItemIdentifierMapper<datafinder.persistence.adapters.webdav_.util}
        """

        NullPrivilegeStorer.__init__(self, identifier)
        self.__connectionPool = connectionPool
        self.__persistenceId = itemIdMapper.mapIdentifier(identifier)
        self.__privilegeMapper = privilegeMapper
        self.__connectionHelper = connectionHelper
        
    def retrievePrivileges(self):
        """ @see: L{NullPrivilegeStorer<datafinder.persistence.privileges.privilegestorer.NullPrivilegeStorer>}"""

        connection = self.__connectionPool.acquire()
        try:
            webdavStorer = self.__connectionHelper.createResourceStorer(self.__persistenceId, connection)
            try:
                privileges = webdavStorer.getCurrentUserPrivileges()
            except WebdavError, error:
                raise PersistenceError(error.reason)
            else:
                return self.__privilegeMapper.mapPersistencePrivileges(privileges)
        finally:
            self.__connectionPool.release(connection)

    def retrieveAcl(self):
        """ @see: L{NullPrivilegeStorer<datafinder.persistence.privileges.privilegestorer.NullPrivilegeStorer>}"""

        connection = self.__connectionPool.acquire()
        try:
            webdavStorer = self.__connectionHelper.createResourceStorer(self.__persistenceId, connection)
            try:
                privileges = webdavStorer.getAcl()
            except WebdavError, error:
                raise PersistenceError(error.reason)
            return self.__privilegeMapper.mapPersistenceAcl(privileges)
        finally:
            self.__connectionPool.release(connection)
    
    def updateAcl(self, acl):
        """ @see: L{NullPrivilegeStorer<datafinder.persistence.privileges.privilegestorer.NullPrivilegeStorer>}"""
        
        connection = self.__connectionPool.acquire()
        try:
            webdavStorer = self.__connectionHelper.createResourceStorer(self.__persistenceId, connection)
            try:
                webdavStorer.setAcl(self.__privilegeMapper.mapAcl(acl))
            except WebdavError, error:
                raise PersistenceError(error.reason)
        finally:
            self.__connectionPool.release(connection)
