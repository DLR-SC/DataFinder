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
Implements different concrete data store configurations.
"""


import base64
from copy import copy, deepcopy
import sys

from datafinder.core.configuration.gen import datastores


__version__ = "$Revision-Id:$" 


_WIN32_PLATFORM = "win32"
_PATH_SEPARATOR = ";"


class DefaultDataStore(object):
    """ Represents the default configuration for data stores. """
    
    _xmlBindingClass = datastores.default
    
    def __init__(self, name=None, storeType=None, iconName="dataStore", url=None, isDefault=False, owner=None, persistedStore=None):
        """ Constructor. """
        
        self._dataLocationUri = None
        self._parameters = dict()
        if persistedStore is None:
            self._store = self._xmlBindingClass(name, storeType, iconName, url, isDefault, owner)
        else:
            self._store = persistedStore
    
    def toPersistenceRepresentation(self):
        """ Returns the persistence representation. """
        
        self._store.__dict__.update(self.__dict__)
        return self._store
    
    def __getattr__(self, name):
        """ Automatically redirects property calls to the generated class. """
        
        return getattr(self._store, name)
    
    def __deepcopy__(self, _):
        """ The deep copy implementation. """
        
        store = self.toPersistenceRepresentation()
        store = deepcopy(store)
        return self.__class__(persistedStore=store)

    def __copy__(self):
        """ The copy implementation. """
        
        store = self.toPersistenceRepresentation()
        store = copy(store)
        return self.__class__(persistedStore=store)

    def __cmp__(self, other):
        """ Implements comparison. """
        
        try:
            return cmp(self.name, other.name)
        except AttributeError:
            return 1

    @property
    def dataLocationUri(self):
        """ 
        Returns the data location URI.
        This is a convenience interface to simplify usage. 
        """ 
        
        return self._dataLocationUri
    
    @property
    def parameters(self):
        """ 
        Returns additional parameters required for storage access.
        This is a convenience interface to simplify usage. 
        """ 
        
        return self._parameters
    
    @property
    def isMigrated(self):
        """ 
        Returns flag indicating whether the data store is migrated or not.
        This is a convenience interface to simplify usage. 
        """ 

        try:
            return len(self.isMigratedTo) > 0
        except AttributeError:
            return False
        
    def _getStorageRealisation(self):
        """ 
        Returns storage realization type.
        This is a convenience interface to simplify usage. 
        """ 

        try:
            return self._store.storageRealisation
        except AttributeError:
            return None

    def _setStorageRealisation(self, value):
        """ 
        Returns storage realization type.
        This is a convenience interface to simplify usage. 
        """ 

        self._store.storageRealisation = value
    storageRealisation = property(_getStorageRealisation, _setStorageRealisation)
        
        
class FileDataStore(DefaultDataStore):
    """ Restricts properties of a File data store configuration. """

    _xmlBindingClass = datastores.file
    
    def __init__(self, name=None, storeType=None, iconName="dataStore", url=None, isDefault=False, owner=None, persistedStore=None):
        """ Constructor. """
        
        DefaultDataStore.__init__(self, name, storeType, iconName, url, isDefault, owner, persistedStore)
        self._password = self._store.password
        self._dataLocationUri = self._determineDataLocationUri()
        self._parameters = self._parameters = {"username": self.username, "password": self.password}
        
    def _determineDataLocationUri(self):
        """ Determines the correct data location. """
        
        if _PATH_SEPARATOR in self.dataLocation:
            windowsLocation, unixLocation = self.dataLocation.split(_PATH_SEPARATOR)
            if sys.platform == _WIN32_PLATFORM:
                return windowsLocation
            else:
                return unixLocation
        else:
            return self.dataLocation
        
    def __getPassword(self):
        """ Getter for the password. """
        
        if self._password is None:
            return None
        else:
            return base64.decodestring(self._password)
        
    def __setPassword(self, value):
        """ Setter for the password. """
        
        if value is None:
            self._password = None
        else:
            try:
                self._password = base64.encodestring(value)
            except Exception:
                raise ValueError("Irregular password has been provided.")
    password = property(__getPassword, __setPassword)
    
    def toPersistenceRepresentation(self):
        """ Overwrites default implementation. """
        
        store = DefaultDataStore.toPersistenceRepresentation(self)
        store.password = self._password
        return store
    
    
class FtpDataStore(DefaultDataStore):
    """ Restricts properties of a FTP data store configuration. """

    _xmlBindingClass = datastores.ftp
    
    def __init__(self, name=None, storeType=None, iconName="dataStore", url=None, isDefault=False, owner=None, persistedStore=None):
        """ Constructor. """
        
        DefaultDataStore.__init__(self, name, storeType, iconName, url, isDefault, owner, persistedStore)
        self._password = self._store.password
        
    def __getPassword(self):
        """ Getter for the password. """
        
        if self._password is None:
            return None
        else:
            return base64.decodestring(self._password)
        
    def __setPassword(self, value):
        """ Setter for the password. """
        
        if value is None:
            self._password = None
        else:
            try:
                self._password = base64.encodestring(value)
            except Exception:
                raise ValueError("Irregular password has been provided.")
    password = property(__getPassword, __setPassword)
    
    def toPersistenceRepresentation(self):
        """ Overwrites default implementation. """
        
        store = DefaultDataStore.toPersistenceRepresentation(self)
        store.password = self._password
        return store
    

class OfflineDataStore(DefaultDataStore):
    """ Restricts properties of an Offline data store configuration. """
    
    _xmlBindingClass = datastores.offlinemedia
    
    def __init__(self, name=None, storeType=None, iconName="dataStore", url=None, isDefault=False, owner=None, persistedStore=None):
        """ Constructor. """
        
        DefaultDataStore.__init__(self, name, storeType, iconName, url, isDefault, owner, persistedStore)
    

class GridFtpDataStore(DefaultDataStore):
    """ Restricts properties of a GridFTP data store configuration. """
    
    _xmlBindingClass = datastores.gridftp
    
    def __init__(self, name=None, storeType=None, iconName="dataStore", url=None, isDefault=False, owner=None, persistedStore=None):
        """ Constructor. """
        
        DefaultDataStore.__init__(self, name, storeType, iconName, url, isDefault, owner, persistedStore)
        self._tcpBufferSize = self._store.tcpBufferSize
        self._parallelConnections = self._store.parallelConnections
    
    def __setTcpbuffersize(self, tcpBufferSize):
        """ Setter for TCP buffer size. """
        
        try:
            intValue = int(tcpBufferSize)
        except (TypeError, ValueError):
            raise ValueError("TCP buffer size has to be an integer value > 0.")
        if intValue <= 0:
            raise ValueError("TCP buffer size has to be an integer value > 0.")
        self._tcpBufferSize = intValue
        
    def __getTcpbuffersize(self):
        """ Getter for TCP buffer size. """
        
        return self._tcpBufferSize
    tcpBufferSize = property(__getTcpbuffersize, __setTcpbuffersize)

    def __setParallelconnections(self, parallelConnections):
        """ Setter for parallel connections. """
        
        try:
            intValue = int(parallelConnections)
        except (TypeError, ValueError):
            raise ValueError("Parallel connections property has to be an integer value >= 0.")
        if intValue < 0:
            raise ValueError("Parallel connections property has to be an integer value >= 0.")
        self._parallelConnections = intValue
        
    def __getParallelconnections(self):
        """ Getter for parallel connections. """
        
        return self._parallelConnections
    parallelConnections = property(__getParallelconnections, __setParallelconnections)

    def toPersistenceRepresentation(self):
        """ Overwrites default implementation. """
        
        store = DefaultDataStore.toPersistenceRepresentation(self)
        store.tcpBufferSize = self._tcpBufferSize
        store.parallelConnections = self._parallelConnections
        return store


class TsmDataStore(DefaultDataStore):
    """ Restricts properties of a File data store configuration. """

    _xmlBindingClass = datastores.tsm
    
    def __init__(self, name=None, storeType=None, iconName="dataStore", url=None, isDefault=False, owner=None, persistedStore=None):
        """ Constructor. """
        
        DefaultDataStore.__init__(self, name, storeType, iconName, url, isDefault, owner, persistedStore)
        self._password = self._store.password
        self._dataLocationUri = "tsm://" + self.clientHostName
        if self.archiveRootDirectory.startswith("/"):
            self._dataLocationUri += self.archiveRootDirectory
        else:
            self._dataLocationUri += "/" + self.archiveRootDirectory
        self._parameters = {"username": self.username, "password": self.password, "serverNodeName": self.serverNodeName}
        
    def __getPassword(self):
        """ Getter for the password. """
        
        if self._password is None:
            return None
        else:
            return base64.decodestring(self._password)
        
    def __setPassword(self, value):
        """ Setter for the password. """
        
        if value is None:
            self._password = None
        else:
            try:
                self._password = base64.encodestring(value)
            except Exception:
                raise ValueError("Irregular password has been provided.")
    password = property(__getPassword, __setPassword)
    
    def toPersistenceRepresentation(self):
        """ Overwrites default implementation. """
        
        store = DefaultDataStore.toPersistenceRepresentation(self)
        store.password = self._password
        return store


class WebdavDataStore(DefaultDataStore):
    """ Restricts properties of a WebDAV data store configuration. """

    _xmlBindingClass = datastores.webdav
    
    def __init__(self, name=None, storeType=None, iconName="dataStore", url=None, isDefault=False, owner=None, persistedStore=None):
        """ Constructor. """
        
        DefaultDataStore.__init__(self, name, storeType, iconName, url, isDefault, owner, persistedStore)
        self._password = self._store.password
        self._dataLocationUri = self.dataLocation
        self._parameters = {"username": self.username, "password": self.password}
        
    def __getPassword(self):
        """ Getter for the password. """
        
        if self._password is None:
            return None
        else:
            return base64.decodestring(self._password)
        
    def __setPassword(self, value):
        """ Setter for the password. """
        
        if value is None:
            self._password = None
        else:
            try:
                self._password = base64.encodestring(value)
            except Exception:
                raise ValueError("Irregular password has been provided.")
    password = property(__getPassword, __setPassword)
    
    def toPersistenceRepresentation(self):
        """ Overwrites default implementation. """
        
        store = DefaultDataStore.toPersistenceRepresentation(self)
        store.password = self._password
        return store


class SubversionDataStore(WebdavDataStore):
    """ Restricts properties of a Subversion data store configuration. """

    _xmlBindingClass = datastores.svn
    
    def __init__(self, name=None, storeType=None, iconName="dataStore", url=None, isDefault=False, owner=None, persistedStore=None):
        """ Constructor. """
        
        WebdavDataStore.__init__(self, name, storeType, iconName, url, isDefault, owner, persistedStore)


class S3DataStore(DefaultDataStore):
    """  Restricts properties of a S3 data store configuration """
    
    _xmlBindingClass = datastores.s3
    
    def __init__(self, name=None, storeType=None, iconName="dataStore", url=None, isDefault=False, owner=None, persistedStore=None):
        """ Constructor. """
        
        DefaultDataStore.__init__(self, name, storeType, iconName, url, isDefault, owner, persistedStore)
        self._password = self._store.password
        self._dataLocationUri = "S3:" + self.dataLocation # datalocation = bucketname
        
        self._parameters = {"username": self.username, "password": self.password}
        
    def __getPassword(self):
        """ Getter for the password. """
        
        if self._password is None:
            return None
        else:
            return base64.decodestring(self._password)
        
    def __setPassword(self, value):
        """ Setter for the password. """
        
        if value is None:
            self._password = None
        else:
            try:
                self._password = base64.encodestring(value)
            except Exception:
                raise ValueError("Irregular password has been provided.")
    password = property(__getPassword, __setPassword)
    
    def toPersistenceRepresentation(self):
        """ Overwrites default implementation. """
        
        store = DefaultDataStore.toPersistenceRepresentation(self)
        store.password = self._password
        return store
