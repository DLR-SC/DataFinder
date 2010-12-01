# pylint: disable=R0201
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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
Implements factory methods for objects that can be used to
access a ZIP archive as repository.
"""

import os
from zipfile import ZipFile, is_zipfile

from datafinder.persistence.adapters.archive.data.adapter import DataArchiveAdapter
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata.metadatastorer import NullMetadataStorer
from datafinder.persistence.privileges.privilegestorer import NullPrivilegeStorer


__version__ = "$Revision-Id:$" 


class FileSystem(object):
    """
    This class implements the FileSystem protocol to act as entry point into
    the archive storage adapter which provides ZIP archive based backups of
    repositories.
    """
    
    def __init__(self, baseConfiguration):
        """ Initialize the archive file system.
        
        The file system is only instantiated here, the opening / creation of the actual
        archive happens during the call to prepareUsage.
        
        @param baseConfiguration: Object specifying configuration options such as the filename
                                  of the archive and the password used for encoding.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
        """

        self._configuration = baseConfiguration
        self._archive = None
        self.readonly = False
    
    def updateCredentials(self, credentials=None):
        """ Set the credentials (i.e. the password) used to encode this file. Therefore the
        'password' field of the credentials dict has to be set.
        
        @param credentials: The login credentials to be used.
        @type credentials: A dict mapping string to string.
        """

        try:
            self._configuration.password = credentials['password']
        except KeyError:
            raise PersistenceError("No password provided.")

    def createDataStorer(self, identifier):
        """ Create an instance of an archive specific DataStorer.
        
        @param identifier: The identifier of the node to be stored.
        @type identifier: string
        """
    
        return DataArchiveAdapter(identifier, self._archive, readonly=self.readonly)
    
    def createMetadataStorer(self, identifier): # R0201
        """ Create an instance of an archive specific MetadataStorer.
        
        @param identifier: The identifier of the node whose properties should be stored.
        @type identifier: string
        """
    
        return NullMetadataStorer(identifier)
    
    def createPrivilegeStorer(self, identifier): # R0201
        """ Dummy method creating nothing. """
    
        return NullPrivilegeStorer(identifier)
    
    @staticmethod
    def hasCustomMetadataSupport():
        """ Returns whether custom meta data are supported (which is True). """
    
        return True
    
    @staticmethod
    def metadataIdentifierPattern():
        """ Returns the pattern to identify meta data. """
        
        return None
    
    @staticmethod
    def hasMetadataSearchSupport():
        """ Returns whether the meta data can be sought (which is False). """
        
        return False
    
    @staticmethod
    def hasPrivilegeSupport():
        """ Returns whether the archive supports privileges (which is False). """
        
        return False

    def release(self):
        """ Release the current archive from usage. This includes closing the ZIP file. """
        
        if self._archive is not None:
            self._archive.close()
            self._archive = None
    
    def prepareUsage(self):
        """ Prepare the current archive for usage. This means that the respective archive
        configured through the configuration.filename variable is either opened for extension
        (if the file already exists) or created.
        """
        
        if not self._archive:
            filename = self._configuration.uriPath
            try:
                if os.path.exists(filename) and is_zipfile(filename):
                    self._archive = ZipFile(filename, "a")
                else:
                    self._archive = ZipFile(filename, "w")
            except IOError, error:
                raise PersistenceError("Unable to create archive. Reason: '%s'" % str(error))
