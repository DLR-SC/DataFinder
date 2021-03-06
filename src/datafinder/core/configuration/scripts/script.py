# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#
#met:
#
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


""" Implements different script representation. """


import atexit
import imp
import sys
import tarfile
import tempfile
import traceback

from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration.scripts import constants
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import createFileStorer


__version__ = "$Revision-Id:$" 


_COMMENT_CHARACTER = "#"
_LIST_SEPARATOR = ","


class Script(object):
    """ Represents a single script extension. """
    
    _logger = getDefaultLogger()
    
    def __init__(self, fileStorer):
        """
        Initialize a new script.
        
        @param fileStorer: Allowing access to the script data.
        @type fileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        """
        
        self._fileStorer = fileStorer
        self.uri = self._fileStorer.uri
        self.name = self._fileStorer.name
        self.location = None
        
        # Script options
        self.title = None
        self.description = None
        self.datatypes = list()
        self.dataformats = list()
        self.iconName = None
        self.version = None
        self.automatic = False
        
        self._parseScript()
        
        if self.iconName is None:
            self.iconName = "lightning_bolt"
            
        if self.title is None:
            self.title = fileStorer.name
    
    def _parseScript(self):
        """ Parse the script and extract the meta data. """

        dataStream = self._fileStorer.readData()
        try:
            try:
                line = dataStream.readline()
                while line:
                    line = line.strip()
                    self._parse(line)
                    line = dataStream.readline()
            finally:
                dataStream.close()
        except IOError:
            raise ConfigurationError("Cannot read script data.")
    
    def _parse(self, line):
        """ Evaluates the line and sets the corresponding script attribute. """
        
        if line.startswith(_COMMENT_CHARACTER):
            if constants.TITLE_KEYWORD in line:
                self.title = line.split(constants.TITLE_KEYWORD)[1].strip()
            elif constants.DATATYPES_KEYWORD in line:
                datatypes = line.split(constants.DATATYPES_KEYWORD)[1].split(_LIST_SEPARATOR)
                for datatype in datatypes:
                    datatype = datatype.strip()
                    if len(datatype) > 0:
                        self.datatypes.append(datatype)
            elif constants.DATAFORMATS_KEYWORD in line:
                dataformats = line.split(constants.DATAFORMATS_KEYWORD)[1].split(_LIST_SEPARATOR)
                for dataformat in dataformats:
                    dataformat = dataformat.strip()
                    if len(dataformat) > 0:
                        self.dataformats.append(dataformat)
            elif constants.ICON_KEYWORD in line:
                self.iconName = line.split(constants.ICON_KEYWORD)[1].strip()
            elif constants.VERSION_KEYWORD in line:
                self.version = line.split(constants.VERSION_KEYWORD)[1].strip()
            elif constants.DESCRIPTION_KEYWORD in line:
                self.description = line.split(constants.DESCRIPTION_KEYWORD)[1].strip()
            elif constants.AUTOMATIC_EXECUTE_KEYWORD in line:
                self.automatic = True
        
    def execute(self):
        """
        Execute the script.
        
        @param scriptOut: Object to write the script output to.
        @type scriptOut: Object with write() method.
        
        @raise ConfigurationError: Raised if execution of script caused
                                   an exception or script terminated with
                                   a negative return code.
        """

        try:
            fileObject = self._fileStorer.readData()
        except PersistenceError, error:
            raise ConfigurationError("Cannot access script.\nReason: '%s'" % error.message)
        else:
            _loadModule(fileObject, self.name, self._logger)
            
    @property
    def isBound(self):
        """ 
        Flag indicating whether the scripts does
        only work with certain data types or formats.
        """
        
        return len(self.dataformats) > 0 or len(self.datatypes) > 0        


class ScriptCollection(object):
    """ Class representing a script collection. """
    
    _logger = getDefaultLogger()
    
    def __init__(self, fileStorer):
        """ 
        Constructor. 
        
        @param fileStorer: Allowing access to the script data.
        @type fileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        """
        
        self._fileStorer = fileStorer
        self.uri = self._fileStorer.uri
        self.name = self._fileStorer.name
        self._tmpdir = tempfile.mkdtemp()
        sys.path.append(self._tmpdir)
        
        self.title = self._fileStorer.name[:-4]
        sys.path.append(self._tmpdir)
        
        self._baseDirFileStorer = createFileStorer("file:///" + self._tmpdir + "/" + self.title)
        atexit.register(self._cleanup)
        
        self.scripts = list()
        self.hasPreferences = False
        self.location = None
        
        self._extract()
        self._parse()

    def _extract(self):
        """ Extract the script collection. """
        
        dataStream = self._fileStorer.readData()
        tar = tarfile.open(fileobj=dataStream)
        for member in tar.getmembers():
            tar.extract(member, self._tmpdir)
        tar.close()
        dataStream.close()
    
    def _parse(self):
        """ Parse all scripts. """
        
        configFileStorer = self._baseDirFileStorer.getChild(constants.SCRIPT_DEFINITION_FILE_NAME)
        data = configFileStorer.readData()
        
        for line in data.readlines():
            fileStorer = self._baseDirFileStorer.getChild(line.strip())
            self.scripts.append(Script(fileStorer))
        data.close()
        
        if self._baseDirFileStorer.getChild(constants.PREFERENCES_PAGE_MODULE_NAME).exists():
            self.hasPreferences = True
    
    def _cleanup(self):
        """ Cleanup the temporary directory. """
        
        if self._tmpdir in sys.path:
            sys.path.remove(self._tmpdir)
        try:
            fileStorer = createFileStorer("file:///" + self._tmpdir)
            if fileStorer.exists():
                fileStorer.delete()
        except PersistenceError, error:
            self._logger.debug(error.message)

    def executePreferences(self):
        """ Execute the preferences page. """
        
        if self.hasPreferences:
            try:
                fileObject = self._baseDirFileStorer.getChild(constants.PREFERENCES_PAGE_MODULE_NAME).readData()
            except PersistenceError, error:
                raise ConfigurationError("Cannot access script.\nReason: '%s'" % error.message)
            else:
                _loadModule(fileObject, constants.PREFERENCES_PAGE_MODULE_NAME, self._logger)


def _loadModule(fileObject, moduleName, logger):
    """ Loads the content of the file object as Python module.
    It only works with real file objects.
    """
    
    try:
        imp.load_module(moduleName, fileObject, fileObject.name, (".py", "r", imp.PY_SOURCE))
    except Exception, error:
        for line in traceback.format_exception(sys.exc_info()[1], sys.exc_info()[0], sys.exc_info()[2]):
            logger.debug(line)
        raise ConfigurationError("Script '%s' terminated with error-code '%s'." % (moduleName, str(error)))
    finally:
        fileObject.close()
           
         
def createScript(scriptFileStorer, location=constants.LOCAL_SCRIPT_LOCATION):
    """
    Returns a parsed script for the given script file storer.
    
    @param scriptFileStorer: Allows access to the script file.
    @type scriptFileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
    @param location: The Location or source of the script. Default is the "local" location.
    @type location: C{unicode}
    
    @return: C{Script} or C{ScriptCollection}
    
    @raise ConfigurationError: Indicating problem during script parsing.
    """
    
    script = None
    if scriptFileStorer.name.endswith(".py"):
        try:
            script = Script(scriptFileStorer)
        except (IOError, PersistenceError), error:
            raise ConfigurationError("Unable to parse script.\nReason: '%s'" % error.message)
    elif scriptFileStorer.name.endswith(".tar"):
        try:
            script = ScriptCollection(scriptFileStorer)
        except (IOError, PersistenceError), error:
            raise ConfigurationError("Unable to parse script collection.\nReason: '%s'" % error.message)
    else:
        raise ConfigurationError("'%s' is no valid script extension." % scriptFileStorer.name)
    script.location = location
    return script
