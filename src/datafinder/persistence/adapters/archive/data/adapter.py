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
This implementation of NullDataStorer can read out of and write into
ZIP compressed archives. 
"""


__version__ = "$Revision-Id$" 


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
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """
        
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
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """

        return not self._readonly
    
    def exists(self):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """
        
        try:
            self._archive.getinfo(self._persistenceId)
        except KeyError:
            return False
        return True
    
    def writeData(self, data):
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """

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
        """ @see:L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}  """

        try:
            return self._archive.open(self._persistenceId, "r", self._password)
        except IOError, error:
            errorMessage = "Cannot access archive member '%s'.\nReason: '%s'" % (self.identifier, error.message)
            raise PersistenceError(errorMessage)
