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
from datafinder.persistence.adapters.svn.error import SVNError


__version__ = "$Revision-Id:$" 


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
    
    def update(self):
        """ Updates the working copy. """
        
        try:
            self._svnUpdateClient.doUpdate(self._repoWorkingCopyFile, SVNRevision.HEAD, True)
        except SVNException, error:
            raise SVNError(error)
        
    def checkin(self, path):
        """ 
        Checkins to the repository.
        
        @param path: Path to checkin.
        @type path: C{unicode} 
        """
        
        try:
            self._svnCommitClient.doCommit([self._repoWorkingCopyFile], False, "", False, True)
        except SVNException, error:
            raise SVNError(error)
        
    def add(self, path):
        """ 
        Marks changes in the working copy for checking in. 
        
        @param path: Path to add.
        @type path: C{unicode}
        """
        
        try:
            self._svnWorkingCopyClient.doAdd(self._repoWorkingCopyFile, True, False, False, SVNDepth.INFINITY, False, False, False)
        except SVNException, error:
            raise SVNError(error)
        
    def delete(self, path):
        """
        Removes a file or directory from the working copy.
        
        @param path: Path to remove.
        @type path: C{unicode}
        """
        
        try:
            self._svnWorkingCopyClient.doDelete(File(path), True, False)
        except SVNException, error:
            raise SVNError(error)
        
    def copy(self, path, destinationPath):
        """
        Copies a file or directory within the working copy.
        
        @param path: Path to copy.
        @type path: C{unicode}
        @param destinationPath: Path to the destination.
        @type destinationPath: C{unicode}
        """
        
        try:
            self._svnCopyClient.doCopy([SVNCopySource(SVNRevision.HEAD, SVNRevision.HEAD, File(path))], \
                                       File(destinationPath), False, True, True)
        except SVNException, error:
            raise SVNError(error)
        
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
            self._svnWorkingCopyClient.doSetProperty(File(path), key, SVNPropertyValue.create(value), False, SVNDepth.EMPTY, ISVNPropertyHandler, None)
        except SVNException, error:
            raise SVNError(error)
        
    def getProperty(self, path, key):
        """
        Gets the property of a file or directory.
        
        @param path: Path where the property should be retrieved.
        @type path: C{unicode}
        @param key: Name of the property.
        @type key: C{unicode}
        """
        
        try:
            propertyData = self._svnWorkingCopyClient.doGetProperty(File(path), key, SVNRevision.HEAD, SVNRevision.HEAD)
            return propertyData.getValue().getString()
        except SVNException, error:
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
        
    @property
    def repoWorkingCopyPath(self):
        """ Returns the working copy path. """
        
        return self._repoWorkingCopyPath
    
    @property
    def repoPath(self):
        """ Returns the repo path. """
        
        return self._repoPath
