# $Filename$ 
# $Authors$
#
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
The pure data part of the SFTP adapter.
"""


__version__ = "$Revision-Id:$" 


import errno
import stat
import StringIO
import tempfile

from paramiko.ssh_exception import SSHException
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.data import datastorer
from datafinder.persistence.adapters.sftp import constants


class SftpDataAdapter(datastorer.NullDataStorer):
    """ Implements the data adapter to access files/directories via SFTP.
    @note: Links are not supported.
    @note: Copying of large collections might be ineffecient
           because files are transferred to the client and then 
           back to the server. However, this is a limitation of SFTP.
    """
    
    def __init__(self, identifier, persistenceIdentifier, 
                 connectionPool, factory, idMapper):
        datastorer.NullDataStorer.__init__(self, identifier)
        
        self._connectionPool = connectionPool
        self._persistenceIdentifier = persistenceIdentifier
        self._factory = factory
        self._idMapper = idMapper
        
    @property
    def isCollection(self):
        connection = self._connectionPool.acquire()
        try:
            return stat.S_ISDIR(connection.stat(self._persistenceIdentifier).st_mode)
        except (IOError, SSHException), error:
            errorMessage = "Cannot determine status of file/collection from host!\nReason: '%s'" % str(error)
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
            
    @property
    def isLeaf(self):
        return not self.isCollection

    @property
    def canAddChildren(self):
        return self.isCollection

    def createCollection(self, recursively=False):
        if recursively:
            self._createMissingParents()
        self._createSingleCollection()

    def _createMissingParents(self):
        parentId = self._idMapper.determineParentId(self.identifier)
        parent = self._factory.createDataStorer(parentId)
        if not parent.exists():
            try:
                parent.createCollection(recursively=True)
            except RuntimeError:
                raise PersistenceError(
                    "Cannot create collection '%s'.\n" % self.identifier,
                    "The collection path is too deeply nested.")
    
    def _createSingleCollection(self):
        connection = self._connectionPool.acquire()
        try:
            connection.mkdir(self._persistenceIdentifier)
        except (IOError, SSHException), error:
            raise PersistenceError(
                "Cannot create collection '%s'. Reason: '%s'" % (self._persistenceIdentifier, error))
        finally:
            self._connectionPool.release(connection)
    
    def createResource(self):
        self.writeData(StringIO.StringIO(""))
        
    def createLink(self, destination):
        raise PersistenceError("Not implemented.")

    def getChildren(self):
        connection = self._connectionPool.acquire()
        try:
            children = list()
            for name in connection.listdir(self._persistenceIdentifier):
                name = name.decode(constants.FILE_NAME_ENCODING, errors="replace")
                child_id = self._idMapper.determineChildId(self.identifier, name)
                children.append(child_id)
            return children
        except (IOError, SSHException), error:
            raise PersistenceError(
                "Cannot retrieve children of item '%s'. Reason: '%s'" % (self._persistenceIdentifier, error))
        finally:
            self._connectionPool.release(connection)

    def exists(self):
        connection = self._connectionPool.acquire()
        try:
            connection.stat(self._persistenceIdentifier)
            return True
        except IOError, error:
            if error.errno == errno.ENOENT:
                return False
            raise PersistenceError(
                "Cannot determine existence of '%s'. Reason: '%s'" % (self._persistenceIdentifier, error))
        finally:
            self._connectionPool.release(connection)

    def delete(self):
        isCollection = self.isCollection
        connection = self._connectionPool.acquire()
        try:
            if isCollection:
                self._deleteCollection(connection)
            else:
                self._deleteLeaf(connection)
        except (IOError, SSHException), error:
            raise PersistenceError(
                "Cannot delete item '%s'. Reason: '%s'" % (self._persistenceIdentifier, error))
        finally:
            self._connectionPool.release(connection)
            
    def _deleteCollection(self, connection):
        emptiedCollections = self._emptyAllCollections(connection)
        self._deleteEmptiedCollections(connection, emptiedCollections)
        
    def _emptyAllCollections(self, connection):
        collections = [self._persistenceIdentifier]
        emptiedCollections = list()
        while collections:
            currentCollection = collections[0]
            for attrs in connection.listdir_attr(currentCollection):
                persistenceId = self._idMapper.determinePersistenceChildId(
                    currentCollection, attrs.filename)
                if not stat.S_ISDIR(attrs.st_mode):
                    connection.remove(persistenceId)
                else:
                    collections.append(persistenceId)
            collections.remove(currentCollection)
            emptiedCollections.append(currentCollection)
        return emptiedCollections
        
    @staticmethod
    def _deleteEmptiedCollections(connection, emptiedCollections):
        emptiedCollections.reverse()
        for collection in emptiedCollections:
            connection.rmdir(collection)
        
    def _deleteLeaf(self, connection):
        connection.remove(self._persistenceIdentifier)

    def copy(self, destination):
        isCollection = self.isCollection
        connection = self._connectionPool.acquire()
        try:
            if isCollection:
                self._copyCollection(connection, destination)
            else:
                self._copyLeaf(destination)
        except (IOError, SSHException), error:
            raise PersistenceError(
                "Cannot copy item '%s'. Reason: '%s'" % (self._persistenceIdentifier, error))
        finally:
            self._connectionPool.release(connection)
            
    def _copyCollection(self, connection, destination):
        collections = [self]
        baseOrginalId = self.identifier
        baseDestinationId = destination.identifier
        while collections:
            currentCollection = collections[0]
            self._createDestinationCollection(currentCollection, baseOrginalId, baseDestinationId)
            self._copyCollectionContent(currentCollection, connection, collections, baseOrginalId, baseDestinationId)
            
    def _createDestinationCollection(self, orgCollection, baseOrginalId, baseDestinationId):
        destCollectionId = orgCollection.identifier.replace(baseOrginalId, baseDestinationId)
        destCollection = self._factory.createDataStorer(destCollectionId)
        destCollection.createCollection()
    
    def _copyCollectionContent(self, orgCollection, connection, collections, baseOrginalId, baseDestinationId):
        orgPersistenceId = self._idMapper.determinePeristenceIdentifier(orgCollection.identifier)
        for attrs in connection.listdir_attr(orgPersistenceId):
            name = attrs.filename.decode(constants.FILE_NAME_ENCODING, errors="replace")
            itemId = self._idMapper.determineChildId(orgCollection.identifier, name)
            itemStorer = self._factory.createDataStorer(itemId)
            if stat.S_ISDIR(attrs.st_mode):
                collections.append(itemStorer)
            else:
                destItemId = itemId.replace(baseOrginalId, baseDestinationId)
                destItemStorer = self._factory.createDataStorer(destItemId)
                data = itemStorer.readData()
                destItemStorer.writeData(data)
        collections.remove(orgCollection)
    
    def _copyLeaf(self, destination):
        data = self.readData()
        destination.writeData(data)

    def move(self, destination):
        connection = self._connectionPool.acquire()
        destPersistenceId = self._idMapper.determinePeristenceIdentifier(destination.identifier)
        try:
            connection.rename(self._persistenceIdentifier, destPersistenceId)
        except (IOError, SSHException), error:
            errorMessage = "Cannot rename item!\nReason: '%s'" % str(error)
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)

    def readData(self):
        connection = self._connectionPool.acquire()
        temporaryFileObject = tempfile.TemporaryFile()
        try:
            temporaryFileObject.seek(0)
            remoteFileObject = connection.open(self._persistenceIdentifier)
            block = remoteFileObject.read(constants.BLOCK_SIZE)
            while block:
                temporaryFileObject.write(block)
                block = remoteFileObject.read(constants.BLOCK_SIZE)
            temporaryFileObject.seek(0)
            return temporaryFileObject
        except (IOError, SSHException), error:
            errorMessage = "Cannot retrieve file from host!\nReason: '%s'" % str(error)
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)

    def writeData(self, data):
        connection = self._connectionPool.acquire()
        try:
            remoteFileObject = connection.open(self._persistenceIdentifier, "w")
            block = data.read(constants.BLOCK_SIZE)
            while block:
                remoteFileObject.write(block)
                block = data.read(constants.BLOCK_SIZE)
        except (IOError, SSHException), sshException:
            errorMessage = "Cannot transfer data to host!\nReason: '%s'" % str(sshException)
            raise PersistenceError(errorMessage)
        finally:
            data.close()
            self._connectionPool.release(connection)
