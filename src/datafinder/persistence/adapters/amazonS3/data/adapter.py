# pylint: disable=W0511, W0221
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
Implements adapter for manipulating a AmazonS3 file system.
"""


import types
import tempfile

from boto.exception import S3ResponseError, S3CreateError, BotoClientError, S3DataError

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.data.datastorer import NullDataStorer


__version__ = "$Revision-Id:$" 


_PROPERTY_NOT_FOUND_MESSAGE = "Property is missing"


class DataS3Adapter(NullDataStorer):
    """ An adapter instance represents an item within the Amazon S3 file system. """

    def __init__(self, identifier, connectionPool, bucketname, keyname):
        """
        Constructor.
        
        @param identifier: Logical identifier of the resource.
        @type identifier: C{unicode}
        @param connectionPool: Connection pool - connection to S3
        @type connectionPool: L{Connection<datafinder.persistence.webdav_.connection_pool.WebdavConnectionPool>}
        """
        # TODO: Definition of identifier in core layer
        # Mappen auf bucketname und keyname --> Path of the item within the file system. - flat store
        # usual url: http://s3.amazonaws.com/[bucket-name]/[object-name]
        NullDataStorer.__init__(self, identifier)
        self._connectionPool = connectionPool
        
        self._bucketname = bucketname
        self._bucket = None
        self._keyname =  keyname
        self._key = None
        
    @property
    def isLeaf(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        if self._keyname == "":
            return False
        else: 
            if self._bucketname == "":
                return False
            else:
                return True
        
    @property
    def isCollection(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorenr.NullDataStorer>} """
     
        if self._keyname == "":
            if self._bucketname == "":
                return False
            else:
                return True
        else:
            return False
        
    @property
    def canAddChildren(self):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        return self.isCollection

    def createResource(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        if self._bucketname == "":
            raise PersistenceError("Cannot create item with empty bucket name.")
        elif self._keyname == "":
            raise PersistenceError("Cannot create item with empty key name.")
        else:
            try:
                self._bucket = self.createCollection()
                self._key = self._bucket.new_key(self._keyname)
                #self._key.key = self._keyname 
                return self._key
            except PersistenceError, error:
                errorMessage = "Cannot create resource '%s'. Reason: '%s'" % (self.identifier, error) 
                raise PersistenceError(errorMessage)
    
            
    def createCollection(self, recursively = False):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        connection = self._connectionPool.acquire()
        try:
            if self._bucketname == '':
                raise PersistenceError("Cannot create item with empty collection(Bucket) name.")
            else:
                try:
                    self._bucket = connection.create_bucket(self._bucketname)
                    return self._bucket
                except (S3ResponseError, S3CreateError), error:
                    errorMessage = u"Cannot create resource '%s'. Reason: '%s'" % (self.identifier, error.reason)
                    raise PersistenceError(errorMessage)
                finally: 
                    if recursively == True:
                        raise PersistenceError("Storing with S3 does not support storing recursively")
                    self._connectionPool.release(connection)
        finally:
            self._connectionPool.release(connection)
              
    def getChildren(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        if self.isLeaf:
            result = list()
            try:
                if not self._bucket:
                    self._bucket = self.createCollection()
                rawresult = self._bucket.get_all_keys()
            except PersistenceError, error:
                errorMessage = u"Cannot retrieve children of item '%s'. Reason: '%s'" % (self.identifier, error.reason)
                raise PersistenceError(errorMessage)
            else:
                result = rawresult # TODO: map to correct return type 
                return result.keyset
        elif self.isCollection:
            
            connection = self._connectionPool.acquire()
            result = list()
            try:
                rawresult = connection.get_all_buckets()
            except S3ResponseError, error: 
                errorMessage = u"Cannot retrieve children of item '%s'. Reason: '%s'" % (self.identifier, error.reason)
                raise PersistenceError(errorMessage)
            else:
                result = rawresult #  TODO: map to correct return type 
                return result.keyset
            finally: 
                self._connectionPool.release(connection)
        else:
            raise PersistenceError('Cannot retrieve children of unkown source')


    def writeData(self, dataStream):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
    
        try:
            self._key = self.createResource()
            if isinstance(dataStream, types.FileType):
                self._key.set_contents_from_file(dataStream.read())
            else:
                self._key.set_contents_from_string(dataStream)
           
        except (S3ResponseError, S3DataError), error:
            errorMessage = "Unable to write data to '%s'. " % self.identifier + \
                               "Reason: %s" % error.reason 
            raise PersistenceError(errorMessage)
          

    def readData(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        try:
            temporaryFileObject = tempfile.TemporaryFile()
            self._key = self.createResource()
            self._key.get_contents_to_file(temporaryFileObject)
            return temporaryFileObject
        except (PersistenceError, S3ResponseError, BotoClientError), error:
            errorMessage = "Unable to read data from '%s'. " % self.identifier + \
                               "Reason: %s" % error.reason
            raise PersistenceError(errorMessage)
        
    def delete(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        if self.isLeaf:
            try:
                self._bucket = self.createCollection()
                self._bucket.delete_key(self._keyname)
            except (PersistenceError, S3ResponseError), error:  
                errorMessage = "Unable to delete item '%s'. " % self.identifier \
                               + "Reason: %s" % error.reason
                raise PersistenceError(errorMessage)        
        elif self.isCollection:
            connection = self._connectionPool.acquire()
            try:
                self._bucket = self.createCollection()
                allKeys = self._bucket.get_all_keys()
                for key in allKeys:
                    self._bucket.delete_key(key)
                connection.delete_bucket(self._bucket)
            except (PersistenceError, S3ResponseError), error:
                errorMessage = "Unable to delete item '%s'. " % self.identifier \
                               + "Reason: %s" % error.reason
                raise PersistenceError(errorMessage)
            finally:
                self._connectionPool.release()
        else:
            raise PersistenceError("Specified identifier is not available and cannot be deleted")
       
    def move(self, destBucket, destKey):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        self.copy(destBucket, destKey)
        if self.isCollection:
            self.delete()
        
            
    def copy(self, destinationBucket, destKey):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        if self._bucketname == destinationBucket:
            raise PersistenceError('Source and destination are the same resource')
        connection = self._connectionPool.acquire()
        try:
            destBucket = connection.create_bucket(destinationBucket) 
            if self.isCollection:
                if not self._bucket:
                    self._bucket = self.createCollection()
                allKeys = self._bucket.get_all_keys()
                for key in allKeys:
                    key.copy(destBucket)
            elif self.isLeaf:
                if not self._bucket:
                    self._bucket = self.createCollection()
                    if not self._key:
                        self._key = self.createResource()
                        self._key.copy(destBucket, destKey)   
            else:
                raise PersistenceError("No valid bucket or key specified") 
       
        except (S3ResponseError, S3CreateError, PersistenceError), error:
            errorMessage = "Unable to move item '%s' to '%s'. " % (self.identifier, destBucket.identifier) \
                               + "Reason: %s" % error.reason
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release()

    def exists(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        exists = True
        collection = self.isCollection
        if collection == True:
            connection = self._connectionPool.acquire()
            try:
                bucket = connection.lookup(self, self._bucketname)   
            except S3ResponseError, error:
                if bucket is None: 
                    exists = False
                else:
                    raise PersistenceError("Cannot determine item existence. Reason: '%s'" % error.reason)
            finally: 
                self._connectionPool.release()
        elif self.isLeaf:
            try: 
                self.createCollection()
                key = self._bucket.get_key(self._keyname)
            except S3ResponseError, error:
                if key is None: 
                    exists = False
                else:
                    raise PersistenceError("Cannot determine item existence. Reason: '%s'" % error.reason)
        else:
            exists = False
        return exists 
    