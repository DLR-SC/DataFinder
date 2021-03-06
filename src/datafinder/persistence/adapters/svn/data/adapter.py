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


import logging
import os
import shutil

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.adapters.svn.error import SubversionError
from datafinder.persistence.adapters.svn import constants
from datafinder.persistence.adapters.svn.util import util
from datafinder.persistence.data.datastorer import NullDataStorer


__version__ = "$Revision-Id$" 


_BLOCK_SIZE = 30000
_log = logging.getLogger()


class DataSubversionAdapter(NullDataStorer):
    """ An adapter instance represents an item within the SVN file system. """

    def __init__(self, identifier, connectionPool):
        """
        Constructor.
        
        @param identifier: Logical identifier of the resource.
        @type identifier: C{unicode}
        @param connectionPool: Connection pool.
        @type connectionPool: L{Connection<datafinder.persistence.svn.
        connection_pool.SVNConnectionPool>}
        """
        
        NullDataStorer.__init__(self, identifier)
        self._connectionPool = connectionPool

    @property
    def linkTarget(self):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """

        connection = self._connectionPool.acquire()
        try:
            return connection.getProperty(
                self.identifier, constants.LINK_TARGET_PROPERTY_NAME)
        except SubversionError:
            try:
                self._updateParentItem(connection)
                return connection.getProperty(
                    self.identifier, constants.LINK_TARGET_PROPERTY_NAME)
            except SubversionError:
                return None
        finally:
            self._connectionPool.release(connection)
        
    def _updateParentItem(self, connection):
        parentId = util.determineParentPath(self.identifier)
        connection.update(parentId)
        
    @property
    def isLink(self):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """

        return not self.linkTarget is None
        
    @property
    def isLeaf(self):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """
        
        return self._determinItemKind(False)
            
    def _determinItemKind(self, checkCollectionKind=True):
        connection = self._connectionPool.acquire()
        if checkCollectionKind:
            checkMethod = connection.isCollection
        else:
            checkMethod = connection.isLeaf
        
        # Perform the check
        try:
            return checkMethod(self.identifier)
        except SubversionError:
            try:
                self._updateParentItem(connection)
                return checkMethod(self.identifier)
            except SubversionError, error:
                errorMessage = u"Cannot determine resource type of '%s'. Reason: '%s'" \
                             % (self.identifier, error)
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
    
    @property
    def isCollection(self):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """
        
        return self._determinItemKind()
    
    @property
    def canAddChildren(self):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        return self.isCollection

    def createLink(self, destination):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """
        
        self.createResource()
        connection = self._connectionPool.acquire()
        try:
            connection.update(self.identifier)
            connection.setProperty(self.identifier, constants.LINK_TARGET_PROPERTY_NAME, 
                                   destination.identifier)
        except SubversionError, error:
            errorMessage = u"Cannot set property. Reason: '%s'" % error
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
            
    def createResource(self):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """

        connection = self._connectionPool.acquire()
        path = connection.workingCopyPath + self.identifier
        try:
            self._updateParentItem(connection)
            if not os.path.exists(path):
                self._createLocalFile(path)
            else:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                self._createLocalFile(path)
            connection.add(self.identifier)
            connection.checkin(self.identifier)
        except OSError, error:
            errorMessage = os.strerror(error.errno)
            raise PersistenceError(errorMessage)
        except SubversionError, error:
            errorMessage = u"Cannot create resource '%s'. Reason: '%s'" % (self.identifier, error)
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
            
    @staticmethod
    def _createLocalFile(path):
        try:
            fd = open(path, "wb")
            fd.close()
        except IOError, error:
            errorMessage = os.strerror(error.errno)
            raise PersistenceError(errorMessage)
        
    def createCollection(self, recursively=False):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """

        if recursively:
            parent = self._getParent()
            if not parent.exists() and parent.identifier != "/":
                parent.createCollection(True)
        
        connection = self._connectionPool.acquire()
        path = connection.workingCopyPath + self.identifier
        try:
            self._updateParentItem(connection)
            if not os.path.exists(path):
                self._createLocalDirectory(path)
            else:
                if not os.path.isdir(path):
                    os.remove(path)
                    self._createLocalDirectory(path)
            connection.add(self.identifier)
            connection.checkin(self.identifier)
        except OSError, error:
            errorMessage = os.strerror(error.errno)
            raise PersistenceError(errorMessage)
        except SubversionError, error:
            errorMessage = u"Cannot create collection '%s'. Reason: '%s'" \
                           % (self.identifier, error)
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
            
    @staticmethod
    def _createLocalDirectory(path):
        os.mkdir(path)
              
    def _getParent(self):
        """ Helper which create the parent data storer. """
  
        parentId = util.determineParentPath(self.identifier)
        return DataSubversionAdapter(parentId, self._connectionPool)

    def getChildren(self):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """
        
        connection = self._connectionPool.acquire()
        try:
            return connection.getChildren(self.identifier)
        except SubversionError, error:
            errorMessage = u"Cannot retrieve children of item '%s'. Reason: '%s'" \
                           % (self.identifier, error)
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
            
    def writeData(self, dataStream):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """
        
        connection = self._connectionPool.acquire()
        try:
            connection.update(self.identifier)
            fd = open(connection.workingCopyPath + self.identifier, "wb")
            try:
                block = dataStream.read(_BLOCK_SIZE)
                while len(block) > 0:
                    fd.write(block)
                    block = dataStream.read(_BLOCK_SIZE)
            finally:
                fd.close()
                dataStream.close()
            connection.checkin(self.identifier)
        except SubversionError, error:
            errorMessage = u"Unable to write data to '%s'. " % self.identifier + \
                           u"Reason: %s" % error
            raise PersistenceError(errorMessage)
        except IOError, error:
            errorMessage = os.strerror(error.errno)
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)

    def readData(self):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """
        
        connection = self._connectionPool.acquire()
        try:
            connection.update(self.identifier)
            return open(connection.workingCopyPath + self.identifier, "rb")
        except IOError, error:
            errorMessage = os.strerror(error.errno)
            raise PersistenceError(errorMessage)
        except SubversionError, error:
            errorMessage = u"Unable to read data from '%s'. " % self.identifier + \
                           u"Reason: %s" % error
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
 
    def delete(self):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """
        
        connection = self._connectionPool.acquire()
        try:
            connection.delete(self.identifier)
        except SubversionError, error:
            errorMessage = u"Unable to delete item '%s'. " % self.identifier \
                           + u"Reason: %s" % error
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)

    def move(self, destination):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """
        
        self.copy(destination)
        self.delete()
            
    def copy(self, destination):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """
        
        connection = self._connectionPool.acquire()
        try:
            connection.copy(self.identifier, destination.identifier)
        except SubversionError, error:
            errorMessage = u"Unable to copy item '%s' to '%s'. " \
                           % (self.identifier, destination.identifier) \
                           + u"Reason: %s" % error
            raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
        
    def exists(self):
        """ @see: L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """

        connection = self._connectionPool.acquire()
        try:
            self._updateParentItem(connection)
            connection.info(self.identifier)
            return True
        except SubversionError:
            return False
        finally:
            self._connectionPool.release(connection)
