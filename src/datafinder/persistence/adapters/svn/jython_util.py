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
Implements a SVN specific data adapter for Jython.
"""


import hashlib
import os

from java.io import File

from org.tmatesoft.svn.core import SVNException, SVNURL, SVNNodeKind, SVNDepth,\
                                   SVNPropertyValue
from org.tmatesoft.svn.core.io import SVNRepositoryFactory
from org.tmatesoft.svn.core.internal.io.dav import DAVRepositoryFactory
from org.tmatesoft.svn.core.internal.io.fs import FSRepositoryFactory
from org.tmatesoft.svn.core.internal.io.svn import SVNRepositoryFactoryImpl
from org.tmatesoft.svn.core.wc import SVNWCUtil, SVNCommitClient, \
                                      SVNUpdateClient, SVNWCClient, SVNRevision,\
                                      SVNCopyClient, SVNCopySource,\
                                      ISVNPropertyHandler

from datafinder.persistence.error import PersistenceError    
from datafinder.persistence.adapters.svn import constants, util
from datafinder.persistence.adapters.svn.error import SVNError


__version__ = "$Revision-Id:$" 


_BLOCK_SIZE = 30000


class JythonSVNDataWrapper(object):
    """ 
    Implements a SVN specific data adapter for Jython.
    """
    
    def __init__(self, repoPath, workingCopyPath, username, password):
        """
        Constructor.
        """
        
        # For using over http:// and https://
        DAVRepositoryFactory.setup() 
        # For using over snv:// and svn+xx://
        SVNRepositoryFactoryImpl.setup()
        # For using over file:///
        FSRepositoryFactory.setup()

        self._username = username
        self._password = password
        self._repoPath = repoPath
        self._repositoryURL = SVNURL.parseURIEncoded(self._repoPath)
        self._md5 = hashlib.md5()
        self._md5.update(self._repoPath)
        self._repoWorkingCopyPath = workingCopyPath + self._md5.hexdigest()
        self._repoWorkingCopyFile = File(self._repoWorkingCopyPath)
        self._repository = None
        self._svnWorkingCopyClient = None
        self._svnCommitClient = None
        self._svnCopyClient = None
        self._svnUpdateClient = None
        try:
            self._repository = SVNRepositoryFactory.create(SVNURL.parseURIDecoded(self._repoPath))
            self._authManager = SVNWCUtil.createDefaultAuthenticationManager(self._username, self._password)
            self._repository.setAuthenticationManager(self._authManager)
            self._svnWorkingCopyClient = SVNWCClient(self._authManager, None)
            self._svnCommitClient = SVNCommitClient(self._authManager, None)
            self._svnCopyClient = SVNCopyClient(self._authManager, None)
            self._svnUpdateClient = SVNUpdateClient(self._authManager, None)
            self._svnUpdateClient.doCheckout(self._repositoryURL, self._repoWorkingCopyFile, SVNRevision.HEAD, SVNRevision.HEAD, True)
        except SVNException, error:
            raise PersistenceError(error)  
    
    def linkTarget(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._svnUpdateClient.doUpdate(self._repoWorkingCopyFile, SVNRevision.HEAD, True)
            linkTargetPropertyData = self._svnWorkingCopyClient.doGetProperty(File(self._repoWorkingCopyPath + path), constants.LINK_TARGET_PROPERTY, \
                                                                  SVNRevision.HEAD, SVNRevision.HEAD)
            linkTarget = linkTargetPropertyData.getValue().getString()
            if len(linkTarget) == 0:
                return None
            else:
                return linkTarget
        except SVNException, error:
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
            nodeKind = self._repository.checkPath(path[1:], -1)
            if nodeKind == SVNNodeKind.FILE:
                return True
            else:
                return False
        except SVNException, error:
            raise SVNError(error)
    
    def isCollection(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            nodeKind = self._repository.checkPath(path[1:], -1)
            if nodeKind == SVNNodeKind.DIR:
                return True
            else:
                return False
        except SVNException, error:
            raise SVNError(error)
    
    def createLink(self, path, destinationPath):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        self.createResource(path)
        try:
            self._svnUpdateClient.doUpdate(self._repoWorkingCopyFile, SVNRevision.HEAD, True)
            self._svnWorkingCopyClient.doSetProperty(File(self._repoWorkingCopyPath + path), constants.LINK_TARGET_PROPERTY, SVNPropertyValue.create(self._repoPath + destinationPath), False, SVNDepth.EMPTY, ISVNPropertyHandler, None)
            self._svnCommitClient.doCommit([self._repoWorkingCopyFile], False, "", False, True)
        except SVNException, error:
            raise SVNError(error)
    
    def createResource(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            fd = open(self._repoWorkingCopyPath + path, "wb")
            fd.close()
            self._svnWorkingCopyClient.doAdd(self._repoWorkingCopyFile, True, False, False, SVNDepth.INFINITY, False, False, False)
            self._svnCommitClient.doCommit([self._repoWorkingCopyFile], False, "", False, True)
        except IOError, error:
            errorMessage = os.strerror(error.errno)
            raise SVNError(errorMessage)
        except SVNException, error:
            raise SVNError(error)
            
    def createCollection(self, path, recursively):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            if recursively:
                parentPath = util.determineParentPath(path)
                if not self.exists(self._repoWorkingCopyPath + parentPath) and parentPath != "/":
                    self.createCollection(parentPath, True)
            os.mkdir(self._repoWorkingCopyPath + path)
            self._svnWorkingCopyClient.doAdd(self._repoWorkingCopyFile, True, False, False, SVNDepth.INFINITY, False, False, False)
            self._svnCommitClient.doCommit([self._repoWorkingCopyFile], False, "", False, True)
        except OSError, error:
            errorMessage = os.strerror(error.errno)
            raise SVNError(errorMessage)
        except SVNException, error:
            os.rmdir(self._repoWorkingCopyPath + path)
            raise SVNError(error)
    
    def getChildren(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            result = list()
            entryList = self._repository.getDir(path[1:], -1, None, None)
            for entry in entryList:
                entryPath = entry.getURL().toString()
                entryPath = entryPath.replace(self._repoPath, "")
                result.append(entryPath) 
            return result
        except SVNException, error:
            raise SVNError(error)
    
    def writeData(self, path, dataStream):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._svnUpdateClient.doUpdate(self._repoWorkingCopyFile, SVNRevision.HEAD, True)
            fd = open(self._repoWorkingCopyPath + path, "wb")
            try:
                block = dataStream.read(_BLOCK_SIZE)
                while len(block) > 0:
                    fd.write(block)
                    block = dataStream.read(_BLOCK_SIZE)
            finally:
                fd.close()
                dataStream.close()
            self._svnCommitClient.doCommit([self._repoWorkingCopyFile], False, "", False, True)
        except IOError, error:
            errorMessage = os.strerror(error.errno)
            raise SVNError(errorMessage)
        except SVNException, error:
            raise SVNError(error)
    
    def readData(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._svnUpdateClient.doUpdate(self._repoWorkingCopyFile, SVNRevision.HEAD, True)
            return open(self._repoWorkingCopyPath + path, "rb")
        except IOError, error:
            errorMessage = os.strerror(error.errno)
            raise SVNError(errorMessage)
        except SVNException, error:
            raise SVNError(error)
    
    def delete(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._svnUpdateClient.doUpdate(self._repoWorkingCopyFile, SVNRevision.HEAD, True)
            self._svnWorkingCopyClient.doDelete(File(self._repoWorkingCopyPath + path), True, False)
            self._svnCommitClient.doCommit([self._repoWorkingCopyFile], False, "", False, True)
        except SVNException, error:
            raise SVNError(error)
    
    def copy(self, path, destinationPath):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """

        try:
            self._svnUpdateClient.doUpdate(self._repoWorkingCopyFile, SVNRevision.HEAD, True)
            self._svnCopyClient.doCopy([SVNCopySource(SVNRevision.HEAD, SVNRevision.HEAD, File(self._repoWorkingCopyPath + path))], \
                                       File(self._repoWorkingCopyPath + destinationPath), False, True, True)
            self._svnCommitClient.doCommit([self._repoWorkingCopyFile], False, "", False, True)
        except SVNException, error:
            raise SVNError(error)
    
    def exists(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        try:
            self._svnUpdateClient.doUpdate(self._repoWorkingCopyFile, SVNRevision.HEAD, True)
            return os.path.exists(self._repoWorkingCopyPath + path)
        except SVNException, error:
            raise SVNError(error)
        
