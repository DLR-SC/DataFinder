#
# Created: 29.06.2009 meinel <michael.meinel@dlr.de>
# Changed: $Id: adapter.py 4550 2010-03-15 14:57:54Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
This implementation of NullDataStorer can read out of and write into
ZIP compressed archives. 
"""


__version__ = "$LastChangedRevision: 4550 $"


import codecs
import types
from zipfile import ZipInfo

from datafinder.persistence.data.datastorer import NullDataStorer
from datafinder.persistence.error import PersistenceError


_ZIP_FILENAME_CODEC = codecs.lookup("CP437")


class DataArchiveAdapter(NullDataStorer, object):
    """ This class implements the L{NullDataStorer} scheme for ZIP archives. """
    
    def __init__(self, identifier, archive, password=None, readonly=False):
        """ Constructor.
        
        @param identifier: The identifier of the associated item.
        @type identifier: C{unicode}
        @type archive: The zip archive that should be used for storage.
        @type archive: C{zipfile.ZipFile}
        @param password: If the archive is encrypted, the password should be given here.
        @type password: C{string}
        @param readonly: Flag whether the archive is opened read-only.
        @type readonly: C{bool}
        """
        
        super(DataArchiveAdapter, self).__init__(identifier)
        self._archive = archive
        self._children = None
        self._password = password
        self._readonly = readonly
        self._persistenceId = _ZIP_FILENAME_CODEC.encode(self.identifier, errors="ignore")[0] #identifier used to access item in zip archive
    
    def getChildren(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        if not self._children:
            self._children = list()
            files = self._archive.namelist()
            for name in files:
                if not isinstance(name, types.UnicodeType):
                    name = _ZIP_FILENAME_CODEC.decode(name, errors="ignore")[0]
                if name.startswith(self.identifier) \
                and name.find("/", len(self.identifier) + 1) < 0:
                    self._children.append(name)
        return self._children
    
    @property
    def canAddChildren(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        return not self._readonly
    
    def exists(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        try:
            self._archive.getinfo(self._persistenceId)
        except KeyError:
            return False
        return True
    
    def writeData(self, data):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        if self._readonly:
            raise PersistenceError(u"Tried to write to read-only archive.")
        try:
            info = self._archive.getinfo(self._persistenceId)
        except KeyError:
            info = ZipInfo(self._persistenceId)
        try:
            self._archive.writestr(info, data.read())
        except IOError, error:
            errorMessage = "Cannot write data of archive member '%s'.\nReason: '%s'" % (self.identifier, error.message)
            raise PersistenceError(errorMessage)

    def readData(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        try:
            return self._archive.open(self._persistenceId, "r", self._password)
        except IOError, error:
            errorMessage = "Cannot access archive member '%s'.\nReason: '%s'" % (self.identifier, error.message)
            raise PersistenceError(errorMessage)
