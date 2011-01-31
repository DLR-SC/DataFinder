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
from datafinder.persistence.adapters.svn import constants, util
from datafinder.persistence.adapters.svn.error import SVNError


__version__ = "$Revision-Id:$" 


_BLOCK_SIZE = 30000


class CPythonSVNDataWrapper(object):
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
        self._repoWorkingCopyPath = workingCopyPath + self._md5.hexdigest()
        try: 
            self._client.checkout(repoPath, self._repoWorkingCopyPath)
        except ClientError, error:
            raise PersistenceError(error)
        
    def _get_login(self, realm, username, may_save):
        """ Login callback function. """
        
        return True, self._username, self._password, False
    
    def _get_log_message(self):
        """ Log message callback function. """
        
        return True, "datafinder"
    
    def _initLocale(self):
        """ Init the locale. """
        
        if sys.platform == "win32":
            locale.setlocale(locale.LC_ALL, "")
        else:
            if "LC_ALL" in os.environ:
                try:
                    locale.setlocale(locale.LC_ALL, os.environ["LC_ALL"])
                    return
                except locale.Error:
                    pass
                
            languageCode, encoding = locale.getdefaultlocale()
            if languageCode is None:
                languageCode = "en_US"
                
            if encoding is None:
                encoding = "UTF-8"
            if encoding.lower() == "utf":
                encoding = "UTF-8"
                
            try:
                locale.setlocale(locale.LC_ALL, "%s.%s" % (languageCode, encoding))
            except locale.Error:
                try:
                    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
                except locale.Error:
                    locale.setlocale(locale.LC_ALL, "C")
    
    def linkTarget(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._client.update(self._repoWorkingCopyPath + path)
            linkTarget = self._client.propget(constants.LINK_TARGET_PROPERTY, self._repoWorkingCopyPath + path)
            if len(linkTarget) == 0:
                return None
            else:
                return linkTarget[path]
        except ClientError, error:
            raise SVNError(error)
    
    def isLink(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        linkTarget = self.linkTarget(path)
        if linkTarget is None:
            return False
        else:
            return True
    
    def isLeaf(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._client.update(self._repoWorkingCopyPath + path)
            entryList = self._client.list(self._repoWorkingCopyPath + path, recurse=False)
            entry = entryList[0]
            if entry[0].kind == pysvn.node_kind.file:
                return True
            else:
                return False
        except ClientError, error:
            raise SVNError(error)
    
    def isCollection(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._client.update(self._repoWorkingCopyPath + path)
            entryList = self._client.list(self._repoWorkingCopyPath + path, recurse=False)
            entry = entryList[0]
            if entry[0].kind == pysvn.node_kind.dir:
                return True
            else:
                return False
        except ClientError, error:
            raise SVNError(error)
    
    def createLink(self, path, destinationPath):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        self.createResource(path)
        try:
            self._client.update(self._repoWorkingCopyPath + path)
            self._client.propset(constants.LINK_TARGET_PROPERTY, self._repoWorkingCopyPath + destinationPath, self._repoWorkingCopyPath + path)
            self._client.checkin(self._repoWorkingCopyPath + path)
        except ClientError, error:
            raise SVNError(error)
    
    def createResource(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            fd = open(self._repoWorkingCopyPath + path, "wb")
            fd.close()
            self._client.add(self._repoWorkingCopyPath + path)
            self._client.checkin(self._repoWorkingCopyPath + path, "")
        except IOError, error:
            errorMessage = os.strerror(error.errno)
            raise SVNError(errorMessage)
        except ClientError, error:
            raise SVNError(error)
    
    def createCollection(self, path, recursively):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            if recursively:
                parentPath = util.determineParentPath(path)
                if not self.exists(self._repoWorkingCopyPath + parentPath) and parentPath != "/":
                    self.createCollection(parentPath, True)
            os.mkdir(self._repoWorkingCopyPath + path)
            self._client.add(self._repoWorkingCopyPath + path)
            self._client.checkin(self._repoWorkingCopyPath + path, "")
        except OSError, error:
            errorMessage = os.strerror(error.errno)
            raise SVNError(errorMessage)
        except ClientError, error:
            os.rmdir(self._repoWorkingCopyPath + path)
            raise SVNError(error)
    
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
            raise SVNError(error)
    
    def writeData(self, path, dataStream):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._client.update(self._repoWorkingCopyPath + path)
            fd = open(self._repoWorkingCopyPath + path, "wb")
            try:
                block = dataStream.read(_BLOCK_SIZE)
                while len(block) > 0:
                    fd.write(block)
                    block = dataStream.read(_BLOCK_SIZE)
            finally:
                fd.close()
                dataStream.close()
            self._client.checkin(self._repoWorkingCopyPath + path, "")
        except IOError, error:
            errorMessage = os.strerror(error.errno)
            raise SVNError(errorMessage)
        except ClientError, error:
            raise SVNError(error)
    
    def readData(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._client.update(self._repoWorkingCopyPath + path)
            return open(self._repoWorkingCopyPath + path, "rb")
        except IOError, error:
            errorMessage = os.strerror(error.errno)
            raise SVNError(errorMessage)
        except ClientError, error:
            raise SVNError(error)
        
    def delete(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._client.update(self._repoWorkingCopyPath + path)
            self._client.remove(self._repoWorkingCopyPath + path)
            self._client.checkin(self._repoWorkingCopyPath + path, "")
        except ClientError, error:
            raise SVNError(error)
    
    def copy(self, path, destinationPath):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._client.update(self._repoWorkingCopyPath + path)
            self._client.copy(self._repoWorkingCopyPath + path, self._repoWorkingCopyPath + destinationPath)
            self._client.checkin([self._repoWorkingCopyPath + path, self._repoWorkingCopyPath + destinationPath], "")
        except ClientError, error:
            raise SVNError(error)
    
    def exists(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._client.update(self._repoWorkingCopyPath)
            return os.path.exists(self._repoWorkingCopyPath + path)
        except ClientError, error:
            raise SVNError(error)
        
        
class CPythonSVNMetadataWrapper(object):
    pass
