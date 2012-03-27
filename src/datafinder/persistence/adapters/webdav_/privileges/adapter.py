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
Implements the privilege adapter.
"""


from webdav import Constants
from webdav.acp import Privilege
from webdav.Connection import WebdavError

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.privileges.privilegestorer import NullPrivilegeStorer
from datafinder.persistence.adapters.webdav_ import util


__version__ = "$Revision-Id:$" 


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
            

class SimplePrivilegeWebdavAdapter(NullPrivilegeStorer):
    """ Used for non-ACP version. It just evaluates the WebDAV options. """
    
    def __init__(self, identifier, connectionPool, itemIdMapper, privilegeMapper, connectionHelper=util):
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
                options = webdavStorer.options()
            except WebdavError, error:
                raise PersistenceError(error.reason)
            else:
                privileges = list()
                if "allow" in options:
                    privileges = self._mapHttpOptionsToPrivileges(options["allow"])
                return privileges
        finally:
            self.__connectionPool.release(connection)
            
    def _mapHttpOptionsToPrivileges(self, allowed):
        raw_privileges = list()
        self._check_read_privilege(allowed, raw_privileges)
        self._check_write_content_privilege(allowed, raw_privileges)
        self._check_write_properties_privilege(allowed, raw_privileges)
        return self.__privilegeMapper.mapPersistencePrivileges(raw_privileges)

    def _check_read_privilege(self, allowed, raw_privileges):
        read_privilege = True
        for read_part_privilege in ["GET", "PROPFIND"]:
            if read_part_privilege not in allowed:
                read_privilege = False
        if read_privilege:
            raw_privileges.append(Privilege(Constants.TAG_READ))
            
    def _check_write_content_privilege(self, allowed, raw_privileges):
        write_content_privilege = True
        for write_part_privilege in ["POST", "DELETE", "COPY", "MOVE"]:
            if write_part_privilege not in allowed:
                write_content_privilege = False
        if write_content_privilege:
            raw_privileges.append(Privilege(Constants.TAG_WRITE_CONTENT))
            
    def _check_write_properties_privilege(self, allowed, raw_privileges):
        if "PROPPATCH" in allowed:
            raw_privileges.append(Privilege(Constants.TAG_WRITE_PROPERTIES))
