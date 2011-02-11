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


import hashlib
import locale
import os
import pysvn
import sys

from pysvn._pysvn_2_6 import ClientError

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.adapters.svn import constants
from datafinder.persistence.adapters.svn.error import SubversionError


__version__ = "$Revision-Id:$" 


class CPythonSubversionDataWrapper(object):
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
        self._md5 = hashlib.md5()
        self._client = pysvn.Client()
        self._client.callback_get_login = self._get_login
        self._client.callback_get_log_message = self._get_log_message
        self._repoPath = repoPath
        self._md5.update(self._repoPath)
        self._repoWorkingCopyPath = workingCopyPath + "/" + self._md5.hexdigest()
        try: 
            self._client.checkout(repoPath, self._repoWorkingCopyPath)
        except ClientError, error:
            raise PersistenceError(error)
        
    def _get_login(self, _, _, _):
        """ Login callback function. """
        
        return True, self._username, self._password, False
    
    def _get_log_message(self):
        """ Log message callback function. """
        
        return True, "datafinder"
    
    def _initLocale(self):
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
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        return self._determineItemKind(path, pysvn.node_kind.file)
    
    def _determineItemKind(self, path, kind):
        """
        Determines the item type.
        
        @param path: Path to determine.
        @type path: C{unicode}
        @param kind: Kind that should be determined. 
        """
        
        try:
            self._client.update(self._repoWorkingCopyPath + path)
            entryList = self._client.list(self._repoWorkingCopyPath + path, recurse=False)
            entry = entryList[0]
            if entry[0].kind == kind:
                return True
            else:
                return False
        except ClientError, error:
            raise SubversionError(error)
    
    def isCollection(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        return self._determineItemKind(path, pysvn.node_kind.dir)
    
    def update(self):
        """ Updates the working copy. """
        
        try:
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
            self._client.checkin(self._repoWorkingCopyPath + path, "",)
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
            self._client.remove(path)
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
            self._client.copy(path, destinationPath)
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
        
        try:
            propertyValue = self._client.propget(key, self._repoWorkingCopyPath + path)
            return propertyValue[self._repoWorkingCopyPath.replace("\\", "/") + path]
        except ClientError, error:
            raise SubversionError(error)
        except KeyError, error:
            raise SubversionError(error)
    
    def getChildren(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """

        try:
            result = list()
            self._client.update(self._repoWorkingCopyPath + path)
            entryList = self._client.list(self._repoWorkingCopyPath + path, recurse=False)
            entryList = entryList[1:]
            for entry in entryList:
                result.append(entry[0].repos_path) 
            return result
        except ClientError, error:
            raise SubversionError(error)

    @property
    def repoWorkingCopyPath(self):
        """ Returns the working copy path. """
        
        return self._repoWorkingCopyPath
    
    @property
    def repoPath(self):
        """ Returns the repo path. """
        
        return self._repoPath
