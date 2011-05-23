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

import atexit
import os
from tempfile import NamedTemporaryFile

from boto.exception import S3ResponseError, S3CreateError, BotoClientError, S3DataError
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.data.datastorer import NullDataStorer


__version__ = "$Revision-Id$" 


_PROPERTY_NOT_FOUND_MESSAGE = "Property is missing"


class DataS3Adapter(NullDataStorer):
    """ An adapter instance represents an item within the Amazon S3 file system. """

    def __init__(self, identifier, connectionPool, bucketname):
        """
        Constructor.
        
        @param identifier: Logical identifier of the resource.
        @type identifier: C{unicode}
        @param connectionPool: Connection pool - connection to S3
        @type connectionPool: L{Connection<datafinder.persistence.amazonS3.connection_pool.S3ConnectionPool>}
        """ 
        
        NullDataStorer.__init__(self, identifier)
        self._connectionPool = connectionPool
        
        self._bucketname = bucketname
        self._bucket = self._getBucket()
        
        self._keyname =  identifier.encode("UTF-8") 
        self._key = None
        import locale
        locale.setlocale(locale.LC_TIME, "C")

    @property
    def isLeaf(self):
        """@see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        if self._keyname == "/":
            return False
        else: 
            return True
        
    @property
    def isCollection(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorenr.NullDataStorer>} """
        if self._keyname == "/":
            return True
        else:
            return False
        
    @property
    def canAddChildren(self):
        """
        @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        return self.isCollection

    def createResource(self):
        """@see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        if self._keyname == "":
            raise PersistenceError("Cannot create item with empty key name.")
        else:
            try:
                if not self._keyname ==  "/":
                    try:
                        self._key = self._bucket.get_key(self._keyname)
                        if not self._key:
                            self._key = self._bucket.new_key(self._keyname) 
                    except S3ResponseError, error:
                        raise PersistenceError("Cannot create resource. Reason: '%s'" % error.error_message)                                       
            except PersistenceError, error:
                errorMessage = "Cannot create resource '%s'. Reason: '%s'" % (self.identifier, error) 
                raise PersistenceError(errorMessage)
        return self._key 
    
    def _getBucket(self):
        "gets the python object representation of the specified bucket"
        bucket = None
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
            return bucket
                
    def getChildren(self):
        """@see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
               
        if self.isCollection:    
            connection = self._connectionPool.acquire()
            result = list()
            try:
                result = self._bucket.get_all_keys()
            except S3ResponseError, error: 
                errorMessage = u"Cannot retrieve children of item '%s'. Reason: '%s'" % (self.identifier, error.reason)
                raise PersistenceError(errorMessage)
            else:
                return result 
                
            finally: 
                self._connectionPool.release(connection)
        else:
            return list()


    def writeData(self, data):
        """@see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
    
        try:
            self._key = self.createResource()
            self._key.set_contents_from_file(data)
        except (S3ResponseError, S3DataError), error:
            errorMessage = "Unable to write data to '%s'. " % self.identifier + \
                               "Reason: %s" % error.error_message
            raise PersistenceError(errorMessage)
          

    def readData(self):
        """@see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            fileObject = NamedTemporaryFile(delete = False)
            self.createResource()
            self._key.get_contents_to_filename(fileObject.name)
            _temporaryFiles.append(fileObject)
            return fileObject
        except (PersistenceError, S3ResponseError, BotoClientError), error:
            errorMessage = "Unable to read data from '%s'. " % self.identifier + \
                               "Reason: %s" % error.reason
            raise PersistenceError(errorMessage)
    

        
           
    def delete(self):
        """@see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """

        if self.isLeaf and not self._keyname.endswith("/"):
            try:
                self.createResource()
                self._key.delete()
            except (PersistenceError, S3ResponseError), error:  
                errorMessage = "Unable to delete item '%s'. " % self.identifier \
                                   + "Reason: %s" % error.reason
                raise PersistenceError(errorMessage)        

        else:
            raise PersistenceError("Specified identifier is not available and cannot be deleted")
       
    def move(self, destination):
        """@see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        self.copy(destination)
        self.delete()
        
    def copy(self, destination):
        """@see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        connection = self._connectionPool.acquire()
        try:
            destination.writeData(self.readData())       
        except (S3ResponseError, S3CreateError, PersistenceError), error:
            errorMessage = "Unable to move item '%s' to '%s'. " % (self.identifier, self._bucket.identifier) \
                               + "Reason: %s" % error.reason
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection) 

    def exists(self):
        """@see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        exists = True
        if self.isCollection:
            if not self._bucket: 
                exists = False       
        elif self.isLeaf:
            connection = self._connectionPool.acquire()
            try: 
                key = self._bucket.get_key(self._keyname)
                if key is None:
                    exists = False
            except S3ResponseError, error:
                raise PersistenceError("Cannot determine item existence. Reason: '%s'" % error.error_message)
            finally: 
                self._connectionPool.release(connection)
        else:
            exists = False
        return exists 

_temporaryFiles = list()
@atexit.register
def _cleanupTemporaryFile():
    """Cleaning up TemporaryFiles for a """
    for tempFile in _temporaryFiles:
        try:
            tempFile.close()
            os.remove(tempFile.name)
        except (OSError, PersistenceError):
            raise PersistenceError("Cannot clean up temporary file '%s'" % tempFile.name)

@atexit.register    
def _resetLocale():
    """Reseting the process wide settings"""
    import locale
    try:
        locale.resetlocale(locale.LC_ALL)
    except:
        locale.setlocale(locale.LC_ALL, "C") # -> safe value

        