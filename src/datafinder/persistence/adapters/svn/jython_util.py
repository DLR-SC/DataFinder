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

from org.tmatesoft.svn.core import SVNException, SVNURL, SVNNodeKind
from org.tmatesoft.svn.core.io import SVNRepositoryFactory
from org.tmatesoft.svn.core.internal.io.dav import DAVRepositoryFactory
from org.tmatesoft.svn.core.internal.io.fs import FSRepositoryFactory
from org.tmatesoft.svn.core.internal.io.svn import SVNRepositoryFactoryImpl
from org.tmatesoft.svn.core.wc import SVNWCUtil, SVNCommitClient, SVNLogClient, \
                                      SVNUpdateClient, SVNWCClient

from datafinder.persistence.error import PersistenceError
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
        self._svnUpdateClient = None
        self._svnLogClient = None
        try:
            self._repository = SVNRepositoryFactory.create(SVNURL.parseURIDecoded(self._repoPath))
            self._authManager = SVNWCUtil.createDefaultAuthenticationManager(self._username, self._password)
            self._repository.setAuthenticationManager()
            self._svnWorkingCopyClient = SVNWCClient(self._authManager, None)
            self._svnCommitClient = SVNCommitClient(self._authManager, None)
            self._svnUpdateClient = SVNUpdateClient(self._authManager, None)
            self._svnLogClient = SVNLogClient(self._authManager, None)
            self._svnUpdateClient.doCheckout(self._repositoryURL, SVNRevision.HEAD, self._repoWorkingCopyFile, True)
        except SVNException, error:
            raise PersistenceError(error)  
    
    def linkTarget(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        path = self._correctPath(path)
    
    def isLink(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        path = self._correctPath(path)
    
    def isLeaf(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
          
        path = self._correctPath(path)
        try:
            nodeKind = self._repository.checkPath(path, -1)
            if nodeKind == SVNNodeKind.FILE:
                return True
            else:
                return False
        except SVNException, error:
            raise SVNError(error)
    
    def isCollection(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        path = self._correctPath(path)
        try:
            nodeKind = self._repository.checkPath(path, -1)
            if nodeKind == SVNNodeKind.DIR:
                return True
            else:
                return False
        except SVNException, error:
            raise SVNError(error)
    
    def createLink(self, path, destinationPath):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        path = self._correctPath(path)
    
    def createResource(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        path = self._correctPath(path)
            
    def createCollection(self, path, recursively):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        path = self._correctPath(path)
    
    def getChildren(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        path = self._correctPath(path)
    
    def writeData(self, path, dataStream):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        path = self._correctPath(path)
    
    def readData(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        path = self._correctPath(path)
    
    def delete(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        pass
    
    def copy(self, path, destinationPath):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        path = self._correctPath(path)
    
    def exists(self, path):
        """ @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>} """
        
        path = self._correctPath(path)
        try:
            nodeKind = self._repository.checkPath(path, -1)
            if nodeKind != SVNNodeKind.NONE:
                return True
            else:
                return False
        except SVNException, error:
            raise SVNError(error)
        
    def _correctPath(self, path):
        return path[1:]
