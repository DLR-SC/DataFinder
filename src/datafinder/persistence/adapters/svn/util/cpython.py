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
Implements a SVN specific data adapter for CPython.
"""


import locale
import os
import pysvn
from pysvn import depth
import sys

from pysvn._pysvn_2_6 import ClientError

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.adapters.svn import constants
from datafinder.persistence.adapters.svn.error import SubversionError


__version__ = "$Revision-Id$" 


class CPythonSubversionWrapper(object):
    """ 
    Implements a SVN specific data adapter for CPython.
    """
    
    def __init__(self, repoPath, workingCopyPath, username, password):
        """
        Constructor.
        """
  
        self._initLocale()        
        self._username = username
        self._password = password
        self._client = pysvn.Client()
        self._loginTries = 0
        self._client.callback_get_login = self._getLogin
        self._client.callback_get_log_message = self._getLogMessage
        self._client.callback_ssl_server_trust_prompt = self._sslServerTrustPrompt
        self._repoPath = repoPath
        self._rootUrl = self._client.root_url_from_path(self._repoPath)
        self._cache = dict() # path: kind, size, has props, created rev, 
        # last changed time, last author
        try: 
            self._repoWorkingCopyPath = workingCopyPath
            self._client.checkout(repoPath, self._repoWorkingCopyPath)
        except ClientError, error:
            raise PersistenceError(error)
        except TypeError, error:
            raise PersistenceError(error)
        
    def _getLogin(self, _, __, ___):
        """ Login callback function. """
        
        if self._loginTries > 0:
            return (False, "", "", False)
        else:
            self._loginTries += 1
            return True, self._username, self._password, False
    
    @staticmethod
    def _getLogMessage():
        """ Log message callback function. """
        
        return True, "datafinder"
    
    @staticmethod
    def _sslServerTrustPrompt(trustData):
        """ SSL trust prompt callback. """
        
        return True, trustData["failures"], True
    
    @staticmethod
    def _initLocale():
        """ Init the locale. """
        
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
    
    def isLeaf(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}. """
        # pylint: disable=E1101
        # E1101: pylint could not resolve the node_kind attribute. 

        return self._determineItemKind(path, pysvn.node_kind.file)
    
    def isCollection(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}. """
        # pylint: disable=E1101
        # E1101: pylint could not resolve the node_kind attribute. 

        return self._determineItemKind(path, pysvn.node_kind.dir)
    
    def _determineItemKind(self, path, kind):
        """
        Determines the item type.
        
        @param path: Path to determine.
        @type path: C{unicode}
        @param kind: Kind that should be determined. 
        """
        
        if path in self._cache:
            entry = self._cache[path]
        else:
            try:
                self._client.update(self._repoWorkingCopyPath + path, depth=depth.empty)
                entry = self._client.list(self._repoWorkingCopyPath + path, recurse=False)[0]
                entry = entry[0]
            except ClientError, error:
                raise SubversionError(error)
        return entry.kind == kind
    
    def update(self):
        """ Updates the working copy. """
        
        try:
            self._client.cleanup(self._repoWorkingCopyPath)
            self._client.update(self._repoWorkingCopyPath)
        except ClientError, error:
            raise SubversionError(error)
        
    def checkin(self, path):
        """ 
        Checkins to the repository.
        
        @param path: Path to checkin.
        @type path: C{unicode} 
        """
        
        try:
            self._client.resolved(self._repoWorkingCopyPath, recurse=True)
            self._client.cleanup(self._repoWorkingCopyPath)
            self._client.checkin(self._repoWorkingCopyPath + path, "")
        except ClientError, error:
            raise SubversionError(error)
        
    def add(self, path):
        """ 
        Marks changes in the working copy for checking in. 
        
        @param path: Path to add.
        @type path: C{unicode}
        """
        
        try:
            self._client.add(self._repoWorkingCopyPath + path, recurse=True)
        except ClientError, error:
            raise SubversionError(error)
        
    def delete(self, path):
        """
        Removes a file or directory from the working copy.
        
        @param path: Path to remove.
        @type path: C{unicode}
        """
        
        try:
            self._client.remove(self._repoPath + path, force=True)
        except ClientError, error:
            raise SubversionError(error)
        
    def copy(self, path, destinationPath):
        """
        Copies a file or directory within the working copy.
        
        @param path: Path to copy.
        @type path: C{unicode}
        @param destinationPath: Path to the destination.
        @type destinationPath: C{unicode}
        """
        
        try:
            self._client.copy(self._repoPath + path, self._repoPath + destinationPath)
        except ClientError, error:
            raise SubversionError(error)
        
    def setProperty(self, path, key, value):
        """
        Sets the property of a file or directory.
        
        @param path: Path where the property should be set.
        @type path: C{unicode}
        @param key: Name of the property.
        @type key: C{unicode}
        @param value: Value of the property.
        @type value: C{unicode}
        """
        
        try:
            self._client.propset(key, value, self._repoWorkingCopyPath + path)
            self.checkin(path)
        except ClientError, error:
            raise SubversionError(error)
        
    def getProperty(self, path, key):
        """
        Gets the property of a file or directory.
        
        @param path: Path where the property should be retrieved.
        @type path: C{unicode}
        @param key: Name of the property.
        @type key: C{unicode}
        """  
        # pylint: disable=E1101
        # E1101: pylint could not resolve the Revision attribute.
        
        try:
            propertyValue = self._client.propget(key, self._repoPath + path, revision=pysvn.Revision(pysvn.opt_revision_kind.head), \
                                                 peg_revision=pysvn.Revision(pysvn.opt_revision_kind.head))
            return propertyValue[self._repoPath + path]
        except ClientError, error:
            raise SubversionError(error)
        except KeyError, error:
            raise SubversionError(error)
    
    def getChildren(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            result = list()
            self._client.update(self._repoWorkingCopyPath + path, depth=depth.files)
            entries = self._client.list(self._repoWorkingCopyPath + path, recurse=False)[1:]
            partToRemoveFromEntry = self._repoPath.replace(self._rootUrl, "")
            for entry in entries:
                path = entry[0].repos_path.replace(partToRemoveFromEntry, "")
                self._cache[path] = entry[0]
                result.append(path) 
            return result
        except ClientError, error:
            raise SubversionError(error)
        
    def info(self, path):
        """
        Gets the information about a file or directory.
        
        @param path: Path to the file or directory information is needed.
        @type path: C{unicode}
        """
        
        if path in self._cache:
            entry = self._cache[path]
        else:
            try:
                self._client.update(self._repoWorkingCopyPath + path, depth=depth.empty)
                entry = self._client.list(self._repoWorkingCopyPath + path, recurse=False)[0]
                entry = entry[0]
            except ClientError, error:
                raise SubversionError(error)
        resultDict = dict()
        resultDict["lastChangedAuthor"] = entry.last_author
        resultDict["lastChangedDate"] = str(entry.time)
        resultDict["size"] = str(entry.size)
        return resultDict

    @property
    def repoWorkingCopyPath(self):
        """ Returns the working copy path. """
        
        return self._repoWorkingCopyPath
    
    @property
    def repoPath(self):
        """ Returns the repo path. """
        
        return self._repoPath
