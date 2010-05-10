# pylint: disable-msg=R0201
# R0201 is disabled in order to correctly implement the interface.
#
# Created: 30.06.2009 meinel <Michael.Meinel@dlr.de>
# Changed: $Id: factory.py 4468 2010-02-22 13:40:12Z meinel $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


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


__version__ = "$LastChangedRevision: 4468 $"


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
