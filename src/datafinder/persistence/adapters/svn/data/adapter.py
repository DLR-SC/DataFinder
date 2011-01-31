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


from datafinder.persistence.error import PersistenceError
from datafinder.persistence.data.datastorer import NullDataStorer
from datafinder.persistence.adapters.svn.error import SVNError


__version__ = "$Revision-Id:$" 


_PROPERTY_NOT_FOUND_MESSAGE = "Property is missing"


class DataSVNAdapter(NullDataStorer):
    """ An adapter instance represents an item within the SVN file system. """

    def __init__(self, identifier, connectionPool, itemIdMapper):
        """
        Constructor.
        
        @param identifier: Logical identifier of the resource.
        @type identifier: C{unicode}
        @param connectionPool: Connection pool.
        @type connectionPool: L{Connection<datafinder.persistence.svn.connection_pool.SVNConnectionPool>}
        @param itemIdMapper: Utility object mapping item identifiers. 
        @type itemIdMapper: L{ItemIdentifierMapper<datafinder.persistence.adapters.svn.util.ItemIdentifierMapper}
        """
        
        NullDataStorer.__init__(self, identifier)
        self._connectionPool = connectionPool
        self._itemIdMapper = itemIdMapper
        self._persistenceId = identifier
        self._name = self._itemIdMapper.determineBaseName(identifier)

    @property
    def linkTarget(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            try:
                connection.linkTarget(self._persistenceId)
            except SVNError, error:
                errorMessage = u"Cannot determine link target of '%s'. Reason: '%s'" % (self.identifier, error)
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
        
    @property
    def isLink(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            try:
                return connection.isLink(self._persistenceId)
            except SVNError, error:
                errorMessage = u"Cannot determine resource type of '%s'. Reason: '%s'" % (self.identifier, error)
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
        
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
                connection.createLink(self._persistenceId, destination.identifier)
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
                    connection.createResource(self._persistenceId)
                except SVNError, error:
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
                    connection.createCollection(self._persistenceId, recursively)
                except SVNError, error:
                    errorMessage = u"Cannot create collection '%s'. Reason: '%s'" % (self.identifier, error)
                    raise PersistenceError(errorMessage)
            finally:
                self._connectionPool.release(connection)
                
    def _getParent(self):
        """ Helper which create the parent data storer. """
        
        parentId = self._itemIdMapper.determineParentPath(self.identifier)
        return DataSVNAdapter(parentId, self._connectionPool, self._itemIdMapper, self._connectionHelper)

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
                connection.writeData(self._persistenceId, dataStream)
            except SVNError, error:
                errorMessage = u"Unable to write data to '%s'. " % self.identifier + \
                               u"Reason: %s" % error
                raise PersistenceError(errorMessage)
            except IOError, error:
                errorMessage = u"Cannot read from stream. Reason: '%s'" % error.message
                raise PersistenceError(errorMessage)
        finally:
            dataStream.close()
            self._connectionPool.release(connection)

    def readData(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            try:
                return connection.readData(self._persistenceId)
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
                connection.delete(self._persistenceId)
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
                destinationPersistenceId = self._itemIdMapper.mapIdentifier(destination.identifier)
                connection.copy(self._persistenceId, destinationPersistenceId)
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
                return connection.exists(self._persistenceId)
            except SVNError, error:
                raise PersistenceError("Cannot determine item existence. Reason: '%s'" % error)
        finally:
            self._connectionPool.release(connection)
