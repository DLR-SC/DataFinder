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

It needs a bucketname from an Amazon S3 bucket. In the bucket the data 
items are stored. A bucket is used similar to a directory. Only that 
collections cannot be created within.

The keys with the identifier of the item are stored in the bucket. 
"""


from atexit import register
from os import remove
from locale import resetlocale, setlocale, LC_TIME, Error
from tempfile import NamedTemporaryFile

from boto.exception import S3ResponseError, S3CreateError, BotoClientError, S3DataError
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.data.datastorer import NullDataStorer


__version__ = "$Revision-Id$" 


UTF_ENCODING = "UTF-8"
LOCALE_TIME = "C"


class DataS3Adapter(NullDataStorer):
    """ An adapter instance represents an item within the Amazon S3 file system. """

    def __init__(self, identifier, connectionPool, bucketname):
        """
        Constructor.
        
        @param identifier: Logical identifier of the resource.
        @type identifier: C{unicode}
        @param connectionPool: Connection pool - connection to S3
        @type connectionPool: L{Connection<datafinder.persistence.amazonS3.connection_pool.S3ConnectionPool>}
        @param bucketname: Name of the bucket in Amazon S3, specified in the data location of the configuration.
        @type bucketname: C{unicode}
        """ 
        
        NullDataStorer.__init__(self, identifier)
        self._connectionPool = connectionPool
        
        self._bucketname = bucketname
        self._bucket = self._getBucket()
        
        self._keyname =  identifier.encode(UTF_ENCODING)
        self._key = None

    def _getBucket(self):
        """ Gets a s3 bucket, to access and store data items on the service """ 
        
        bucket = None
        setlocale(LC_TIME, LOCALE_TIME)
        connection = self._connectionPool.acquire()
        try:
            
            bucket = connection.lookup(self._bucketname)
            
        except S3ResponseError, error:
            raise PersistenceError("Cannot determine item existence. Reason: '%s'" % error.error_message)
        else:
            if bucket is None: 
                try:
                    bucket = connection.create_bucket(self._bucketname)
                except (S3ResponseError, S3CreateError), error:
                    errorMessage = u"Cannot create resource '%s'. Reason: '%s'" % (self.identifier, error.error_message)
                    raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
            self._resetLocale()
        return bucket
    
    @property
    def isLeaf(self):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        if self._isRoot(self._keyname):
            return False
        else: 
            return True
     
    def _isRoot(self, key):  
        """ Determines if the root is accessed. """
        
        return key == "/"
    
    @property
    def isCollection(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorenr.NullDataStorer>} """
        
        if self._keyname == "/":
            return True
        else:
            return False
        
    @property
    def canAddChildren(self):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        return self.isCollection

    def createResource(self):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        setlocale(LC_TIME, LOCALE_TIME)
        connection = self._connectionPool.acquire()
        try:
            if not self._keyname ==  "/":
                self._key = self._bucket.get_key(self._keyname)
                if not self._key:
                    self._key = self._bucket.new_key(self._keyname)                                    
        except (S3ResponseError, PersistenceError), error:
            errorMessage = "Cannot create resource '%s'. Reason: '%s'" % (self.identifier, error) 
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
            self._resetLocale()
        return self._key 
                
    def getChildren(self):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        result = list()      
        if self.isCollection:    
            setlocale(LC_TIME, LOCALE_TIME)
            connection = self._connectionPool.acquire()
            try:
                result = self._bucket.get_all_keys()
            except S3ResponseError, error: 
                errorMessage = u"Cannot retrieve children of item '%s'. Reason: '%s'" % (self.identifier, error.reason)
                raise PersistenceError(errorMessage)
            finally: 
                self._connectionPool.release(connection)
                self._resetLocale()
        return result

    def writeData(self, data):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        setlocale(LC_TIME, LOCALE_TIME)
        connection = self._connectionPool.acquire()
        try:
            self._key = self.createResource()
            self._key.set_contents_from_file(data)
        except (S3ResponseError, S3DataError), error:
            errorMessage = "Unable to write data to '%s'. " % self.identifier \
                           + "Reason: %s" % error.error_message
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection) 
            self._resetLocale() 
        
    def readData(self):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        setlocale(LC_TIME, LOCALE_TIME)
        connection = self._connectionPool.acquire()
        try:
            fileObject = NamedTemporaryFile(delete=False)
            self.createResource()
            self._key.get_contents_to_filename(fileObject.name)
            _temporaryFiles.append(fileObject)
            return fileObject
        except (PersistenceError, S3ResponseError, BotoClientError), error:
            errorMessage = "Unable to read data from '%s'. " % self.identifier \
                           + "Reason: %s" % error.reason
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection) 
            self._resetLocale() 
    
    def delete(self):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        if self.isLeaf:
            setlocale(LC_TIME, LOCALE_TIME)
            connection = self._connectionPool.acquire()
            try:
                self.createResource()
                self._key.delete()
            except (PersistenceError, S3ResponseError), error:  
                errorMessage = "Unable to delete item '%s'. " % self.identifier \
                               + "Reason: %s" % error.reason
                raise PersistenceError(errorMessage)     
            finally:
                self._connectionPool.release(connection) 
                self._resetLocale()   
        else:
            raise PersistenceError("Unable to delete item '%s'. " % self.identifier)
       
    def move(self, destination):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        self.copy(destination)
        self.delete()
        
    def copy(self, destination):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        setlocale(LC_TIME, LOCALE_TIME)
        connection = self._connectionPool.acquire()
        try:
            destination.writeData(self.readData())       
        except (S3ResponseError, S3CreateError, PersistenceError), error:
            errorMessage = "Unable to move item '%s' to '%s'." %(self.identifier, self._bucket.identifier)\
                           + "Reason: %s" % error.reason
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection) 
            self._resetLocale()

    def exists(self):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        exists = True
        if self.isLeaf:
            setlocale(LC_TIME, LOCALE_TIME)
            connection = self._connectionPool.acquire()
            try: 
                key = self._bucket.get_key(self._keyname)
                if key is None:
                    exists = False
            except S3ResponseError, error:
                raise PersistenceError("Cannot determine item existence. " \
                                       + "Reason: '%s'" % error.error_message)
            finally: 
                self._connectionPool.release(connection)
                self._resetLocale()
        return exists 

    def _resetLocale(self):
        """Reseting the process time settings"""
        
        try:
            resetlocale(LC_TIME)
        except Error:
            setlocale(LC_TIME, "C")

        
_temporaryFiles = list()

        
@register
def _cleanupTemporaryFile():
    """Cleaning up TemporaryFiles, Problems are sent to the debug logger""" #neu
    
    for tempFile in _temporaryFiles:
        try:
            tempFile.close()
            remove(tempFile.name)
        except (OSError, PersistenceError):
            # sent problem to logger
            raise PersistenceError("Cannot clean up temporary file '%s'" % tempFile.name)
        