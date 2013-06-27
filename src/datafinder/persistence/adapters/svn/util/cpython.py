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
Implements utility functionality for accessing a Subversion repositories.
This implementation works with CPython and is based on C[pysvn}.
"""


import locale
import logging
import os
import pysvn
import sys
import threading

from pysvn import ClientError

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.adapters.svn import constants
from datafinder.persistence.adapters.svn.error import SubversionError
from datafinder.persistence.adapters.svn.util.util import pepareSvnPath


__version__ = "$Revision-Id$" 


_logger = logging.getLogger()


class CPythonSubversionWrapper(object):
    """ 
    Implements CPython specific utility class for accessing SVN repositories.
    """

    def __init__(self, repositoryUri, workingCopyPath, username, password):
        """ Initializes the pysvn client for repository access and performs the initial
        checkout if it does not already exist. """
        
        self._username = username
        self._password = password
        self._workingCopyPath = workingCopyPath
        self._workingPathLength = len(workingCopyPath)
        self._sharedState = None
        
        self._client = pysvn.Client()
        self._client.exception_style = 1 # errors have tuple args: (full msg, list((msg, error code)))
        self._loginTries = 0
        self._client.callback_get_login = self._getLogin
        self._client.callback_get_log_message = lambda: (True, "")
        self._client.callback_ssl_server_trust_prompt = \
            lambda trustData: (True, trustData["failures"], True)
        self._repositoryUri = repositoryUri
        
    def _getLogin(self, _, __, ___):
        """ Provides the login information for the pysvn
        client. """
        
        if self._loginTries > 0:
            return (False, "", "", False)
        else:
            self._loginTries += 1
            return (True, self._username, self._password, False)
        
    def initializeWorkingCopy(self):
        """ Checks the working copy out if it does not exist. """
        
        try:
            if not os.path.exists(self._workingCopyPath):
                self._client.checkout(self._repositoryUri, self._workingCopyPath)
        except ClientError, error:
            raise PersistenceError(error)
                
    def isLeaf(self, path):
        """ Indicates whether the item is a file or not. """
        # pylint: disable=E1101
        # E1101: pylint could not resolve the node_kind attribute. 

        return self._determineItemKind(path, pysvn.node_kind.file)
    
    def isCollection(self, path):
        """ Indicates whether the item is a directory or not. """
        # pylint: disable=E1101
        # E1101: pylint could not resolve the node_kind attribute. 

        return self._determineItemKind(path, pysvn.node_kind.dir)

    def _determineItemKind(self, path, kind):
        """ Determines whether the item is of the given kind. """
        # pylint: disable=E1101
        # E1101: pylint could not resolve the node_kind attribute.
        
        entry = self._determineInfo(path)
        return entry.kind == kind
    
    def update(self, path):
        """ Updates the working copy. 
        This method is synchronized among different connections.
        The update call also restores accidently deleted files (mode: infinity).
        """
        # pylint: disable=E1101
        # E1101: pylint could not resolve the depth attribute.
            
        self._sharedState.lock.acquire()
        try:
            try:
                self._client.cleanup(self.workingCopyPath)
                self._client.revert(self._workingCopyPath + path, True)
                self._client.update(self._workingCopyPath + path, depth=pysvn.depth.infinity )
            except ClientError, error:
                raise SubversionError(error)
        finally:
            self._sharedState.lock.release()
    
    def checkin(self, path):
        """ Commits changes of the item identified with C{path}. It also
        ensures that existing conflicts are resolved.
        """
        
        try:
            self._client.checkin(self._workingCopyPath + path, "")
        except ClientError, error:
            raise SubversionError(error)
        else:
            self._sharedState.removeFromCache(path)
        
    def add(self, path):
        """ Adds a new file/directory to the working copy. """
        
        try:
            self._client.add(self._workingCopyPath + path, recurse=True)
        except ClientError, error:
            raise SubversionError(error)
        
    def delete(self, path):
        """ Removes a file or directory from the repository. It works
        directly on the server, i.e. no call to C{checkin} is required.
        The cached information of the item all removed as well.
        """
        
        try:
            self._client.remove(self._getEncodedUri(path), force=True)
        except ClientError, error:
            raise SubversionError(error)
        else:
            self._sharedState.removeFromCache(path)
        
    def _getEncodedUri(self, path):
        """ Helper method - First the path is encoded to UTF-8 and then
        the special characters are quoted. It returns the 
        full repository URI. It assumes that the repository URI is already in 
        the correctly quoted and encoded format. """

        return self._repositoryUri + pepareSvnPath(path)
        
    def copy(self, path, destinationPath):
        """ The copying process is directly performed on the SVN server. """
        
        try:
            self._client.copy(self._getEncodedUri(path), 
                              self._getEncodedUri(destinationPath))
        except ClientError, error:
            raise SubversionError(error)

    def setProperty(self, path, key, value):
        """
        Sets the property of a file or directory.
        
        @param key: Name of the property.
        @type key: C{unicode}
        @param value: Value of the property.
        @type value: C{unicode}
        """
        
        try:
            self._client.propset(key, value, self._workingCopyPath + path)
            self.checkin(path)
        except ClientError, error:
            raise SubversionError(error)
        
    def getProperty(self, path, name):
        """
        Gets the property value of a file or directory.
        
        @param name: Name of the property.
        @type name: C{unicode}
        
        @rtype: C{unicode}
        """  
        # pylint: disable=E1101
        # E1101: pylint could not resolve the Revision attribute.
        
        result = None
        fullWorkingPath = (self._workingCopyPath + path).encode(constants.UTF8)

        try:
            propertyValues = self._client.propget(
                name, fullWorkingPath, revision=pysvn.Revision(pysvn.opt_revision_kind.working),
                depth=pysvn.depth.empty)
            if fullWorkingPath in propertyValues:
                result = unicode(propertyValues[fullWorkingPath], constants.UTF8)
        except ClientError, error:
            raise SubversionError(error)
        else:
            return result
    
    def getChildren(self, path):
        """ Determines the direct children of the given directory. In prior an
        update is performed. The retrieved information are cached. This method 
        is synchronized among different connections. """
        
        self._sharedState.lock.acquire()
        try:
            try:
                self.update(path)
                children = list()
                entries = self._client.list(self._workingCopyPath + path, recurse=False)
                for entry in entries:
                    entryPath = entry[0].path[self._workingPathLength:]
                    formerEntry = self._sharedState.getFromCache(path)
                    if formerEntry is None:
                        newEntry =  _Info(entry[0])
                    else:
                        newEntry = _Info(entry[0])
                        newEntry.logMessage = formerEntry.logMessage # creation date and owner do not change
                    self._sharedState.addToCache(entryPath, newEntry)
                    children.append(entryPath)
                del children[0] # First item is always the queried path
                return children
            except ClientError, error:
                raise SubversionError(error)
        finally:
            self._sharedState.lock.release()
        
    def info(self, path):
        """ Returns a C{dict} holding the information about:
        - "lastChangedDate", "size", "owner", "creationDate".
        """
        # pylint: disable=E1101
        # E1101: pylint could not resolve the opt_revision_kind attribute.
        
        info = self._determineInfo(path)
            
        if info.logMessage is None: # determine creation date and owner
            try:
                info.logMessage = self._client.log(
                    self._workingCopyPath + path, 
                    revision_start=pysvn.Revision(pysvn.opt_revision_kind.number, 1),
                    revision_end=pysvn.Revision(pysvn.opt_revision_kind.head), limit=1)[0]
            except ClientError, error:
                raise SubversionError(error)
        
        result = dict()
        result["lastChangedDate"] = str(info.lastChangedDate)
        result["size"] = str(info.size)
        result["owner"] = info.owner
        result["creationDate"] = str(info.creationTime)
        return result

    def _determineInfo(self, path):
        """ Retrieves the entry information and puts it into the 
        cache or uses the cached information. """
        
        entry = self._sharedState.getFromCache(path)
        if entry is None:
            try:
                entry = self._client.list(self._workingCopyPath + path, 
                                          recurse=False)[0][0]
                entry = _Info(entry)
                self._sharedState.addToCache(path, entry)
                return entry
            except ClientError, error:
                raise SubversionError(error)
        return entry

    @property
    def canBeAccessed(self):
        try:
            self._client.log(self._repositoryUri)
            return True
        except ClientError, error:
            _logger.debug(error.args[0])
            for _, errorCode in  error.args[1]:
                if errorCode == 160006: # We have no commit in the repository, but its ok.
                    return True
            return False
        
    @property
    def workingCopyPath(self):
        return self._workingCopyPath
    

class _Info(object):
    """ Represents the information of a single item. """
    
    def __init__(self, entry):
        """ Uses a C{PysvnList} and pysvn log message 
        dictionaries as basis and provides a common interface. """
        
        self.lastChangedDate = entry.time
        self.size = entry.size
        self.kind = entry.kind
        self.logMessage = None
        
    @property
    def creationTime(self):
        if not self.logMessage is None :
            return self.logMessage["date"]
        
    @property
    def owner(self):
        if not self.logMessage is None:
            return self.logMessage["author"]
        
        
class _SharedState(object):
    """ Holds the synchronization information.
    This includes a shared lock and a thread-safe
    cache for sharing item information. Items are 
    identified by the their path relative to the
    repository working copy."""
     
    def __init__(self):
        self._lock = threading.RLock()
        self._cache = dict()
        self.lock = threading.RLock()
        
    def addToCache(self, path, info):
        self._lock.acquire()
        try:
            self._cache[path] = info
        finally:
            self._lock.release()
    
    def getFromCache(self, path):

        self._lock.acquire()
        try:
            if path in self._cache:
                return self._cache[path]
        finally:
            self._lock.release()
            
    def removeFromCache(self, path):
        self._lock.acquire()
        try:
            for key in self._cache.keys():
                if key.startswith(path):
                    del self._cache[key]
        finally:
            self._lock.release()

# Used to synchronize repository-specific connections
# which are working on ONE working copy
_repositoryUriSharedStateMap = dict()


def createCPythonWrapper(repositoryUri, workingCopyPath, username, password):
    """ Factory method for safe creation of SVN connections.
    
    Adds specific shared shared state to synchronize work of different 
    connection instances. 
    
    @note: It is expected that the calling client code ensures thread-safety. E.g.,
    by using the default connection pool for connection creation.
    """
    
    connection = CPythonSubversionWrapper(repositoryUri, workingCopyPath, username, password)
    if repositoryUri in _repositoryUriSharedStateMap:
        connection._sharedState = _repositoryUriSharedStateMap[repositoryUri]
    else:
        sharedState = _SharedState()
        connection._sharedState = _SharedState()
        _repositoryUriSharedStateMap[repositoryUri] = sharedState
    return connection


def _initializeLocale():
    """ Initializes encoding information of C{locale} module. """
    
    if sys.platform == constants.WIN32:
        locale.setlocale(locale.LC_ALL, "")
    else:
        if constants.LC_ALL in os.environ:
            try:
                locale.setlocale(locale.LC_ALL, os.environ[constants.LC_ALL])
                return
            except locale.Error:
                # First try did not work, encoding must be set first then set locale.
                pass
        languageCode, encoding = locale.getdefaultlocale()
        if languageCode is None:
            languageCode = "en_US"
        # Set the encoding of the Python environment if no encoding is set.
        if encoding is None:
            encoding = constants.UTF8
        if encoding.lower() == "utf":
            encoding = constants.UTF8
        try:
            locale.setlocale(locale.LC_ALL, "%s.%s" % (languageCode, encoding))
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
            except locale.Error:
                locale.setlocale(locale.LC_ALL, "C")

_initializeLocale() # Just once executed when the module is imported
