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
Implements adapter for manipulating a SVN file system.
"""

import os

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.data.datastorer import NullDataStorer
from datafinder.persistence.adapters.svn.error import SVNError
from datafinder.persistence.adapters.svn import constants
from datafinder.persistence.adapters.svn.util import util


__version__ = "$Revision-Id:$" 


_BLOCK_SIZE = 30000


class DataSVNAdapter(NullDataStorer):
    """ An adapter instance represents an item within the SVN file system. """

    def __init__(self, identifier, connectionPool):
        """
        Constructor.
        
        @param identifier: Logical identifier of the resource.
        @type identifier: C{unicode}
        @param connectionPool: Connection pool.
        @type connectionPool: L{Connection<datafinder.persistence.svn.connection_pool.SVNConnectionPool>}
    
        """
        
        NullDataStorer.__init__(self, identifier)
        self._connectionPool = connectionPool
        self._persistenceId = util.mapIdentifier(identifier)
        self._name = util.determineBaseName(identifier)

    @property
    def linkTarget(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            try:
                connection.update()
                linkTarget = connection.getProperty(constants.LINK_TARGET_PROPERTY, connection.repoWorkingCopyPath + self._persistenceId)
                if len(linkTarget) == 0:
                    return None
                else:
                    return linkTarget
            except SVNError, error:
                errorMessage = u"Cannot determine link target of '%s'. Reason: '%s'" % (self.identifier, error)
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
        
    @property
    def isLink(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        linkTarget = self.linkTarget()
        if linkTarget is None:
            return False
        else:
            return True
        
    @property
    def isLeaf(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            try:
                return connection.isLeaf(self._persistenceId)
            except SVNError, error:
                errorMessage = u"Cannot determine resource type of '%s'. Reason: '%s'" % (self.identifier, error)
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
        
    @property
    def canAddChildren(self):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        return self.isCollection

    @property
    def isCollection(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            try:
                return connection.isCollection(self._persistenceId)
            except SVNError, error:
                errorMessage = u"Cannot determine resource type of '%s'. Reason: '%s'" % (self.identifier, error)
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)

    def createLink(self, destination):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        self.createResource()
        connection = self._connectionPool.acquire()
        try:
            try:
                connection.update()
                connection.setProperty(connection.repoWorkingCopyPath + self._persistenceId, constants.LINK_TARGET_PROPERTY, connection.repoPath + destination.identifier)
                connection.checkin(self._persistenceId)
            except SVNError, error:
                errorMessage = u"Cannot set property. Reason: '%s'" % error
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
            
    def createResource(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        if len(self._name) == 0:
            raise PersistenceError("Cannot create item with empty resource name.")
        else:
            connection = self._connectionPool.acquire()
            try:
                try:
                    fd = open(connection.repoWorkingCopyPath + self._persistenceId, "wb")
                    fd.close()
                    connection.add(self._persistenceId)
                    connection.checkin(self._persistenceId)
                except IOError, error:
                    errorMessage = os.strerror(error.errno)
                    raise PersistenceError(errorMessage)
                except SVNError, error:
                    os.remove(connection.repoWorkingCopyPath + self._persistenceId)
                    errorMessage = u"Cannot create resource '%s'. Reason: '%s'" % (self.identifier, error)
                    raise PersistenceError(errorMessage)
            finally:
                self._connectionPool.release(connection)
            
    def createCollection(self, recursively=False):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        if len(self._name) == 0:
            raise PersistenceError("Cannot create item with empty resource name.")
        else:
            connection = self._connectionPool.acquire()
            try:
                try:
                    if recursively:
                        parent = self._getParent()
                        if not parent.exists():
                            parent.createCollection(True)
                    os.mkdir(connection.repoWorkingCopyPath + self._persistenceId)
                    connection.add(self._persistenceId)
                    connection.checkin(self._persistenceId)
                except OSError, error:
                    errorMessage = os.strerror(error.errno)
                    raise PersistenceError(errorMessage)
                except SVNError, error:
                    errorMessage = u"Cannot create collection '%s'. Reason: '%s'" % (self.identifier, error)
                    raise PersistenceError(errorMessage)
            finally:
                self._connectionPool.release(connection)
                
    def _getParent(self):
        """ Helper which create the parent data storer. """
  
        parentId = self._determineParentPath(self._persistenceId)
        return DataSVNAdapter(parentId, self._connectionPool)
    
    def _determineParentPath(self, path):
        """ 
        Determines the parent path of the logical path. 
       
        @param path: The path.
        @type path: C{unicode}
      
        @return: The parent path of the identifier.
        @rtype: C{unicode}
        """
       
        parentPath = "/".join(path.rsplit("/")[:-1])
        if parentPath == "" and path.startswith("/") and path != "/":
            parentPath = "/"
        return parentPath

    def getChildren(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            try:
                return connection.getChildren(self._persistenceId)
            except SVNError, error:
                errorMessage = u"Cannot retrieve children of item '%s'. Reason: '%s'" % (self.identifier, error)
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
            
    def writeData(self, dataStream):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            try:
                connection.update()
                fd = open(connection.repoWorkingCopyPath + self._persistenceId, "wb")
                try:
                    block = dataStream.read(_BLOCK_SIZE)
                    while len(block) > 0:
                        fd.write(block)
                        block = dataStream.read(_BLOCK_SIZE)
                finally:
                    fd.close()
                    dataStream.close()
                connection.checkin(self._persistenceId)
            except SVNError, error:
                errorMessage = u"Unable to write data to '%s'. " % self.identifier + \
                               u"Reason: %s" % error
                raise PersistenceError(errorMessage)
            except IOError, error:
                errorMessage = u"Cannot read from stream. Reason: '%s'" % error.message
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)

    def readData(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            try:
                connection.update()
                return open(connection.repoWorkingCopyPath + self._persistenceId, "rb")
            except IOError, error:
                errorMessage = os.strerror(error.errno)
                raise PersistenceError(errorMessage)
            except SVNError, error:
                errorMessage = u"Unable to read data from '%s'. " % self.identifier + \
                               u"Reason: %s" % error
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
 
    def delete(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            try:
                connection.update()
                connection.delete(connection.repoWorkingCopyPath + self._persistenceId)
                connection.checkin(self._persistenceId)
            except SVNError, error:
                errorMessage = u"Unable to delete item '%s'. " % self.identifier \
                               + u"Reason: %s" % error
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)

    def move(self, destination):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        self.copy(destination)
        self.delete()
            
    def copy(self, destination):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            try:
                destinationPersistenceId = util.mapIdentifier(destination.identifier)
                connection.update()
                connection.copy(connection.repoWorkingCopyPath + self._persistenceId, connection.repoWorkingCopyPath + destinationPersistenceId)
                connection.checkin(self._persistenceId)
                connection.checkin(destinationPersistenceId)
            except SVNError, error:
                errorMessage = u"Unable to copy item '%s' to '%s'. " % (self.identifier, destination.identifier) \
                               + u"Reason: %s" % error
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
        
    def exists(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        try:
            connection = self._connectionPool.acquire()
            try:
                connection.update()
                return os.path.exists(connection.repoWorkingCopyPath + self._persistenceId)
            except SVNError, error:
                raise PersistenceError("Cannot determine item existence. Reason: '%s'" % error)
        finally:
            self._connectionPool.release(connection)
