# pylint: disable-msg=W0122
#
# Initialization, administration, execution and control of DataFinder scripts.
#
# Created: Heinrich Wendel (heinrich.wendel@dlr.de)
#
# Version: $Id: script.py 4579 2010-03-30 14:22:33Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


""" Implements different script representation. """


import atexit
import sys
import tarfile
import tempfile
import traceback

from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration.scripts import constants
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import createFileStorer


__version__ = "$LastChangedRevision: 4579 $"


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
        
        self.title = None          # scrtitle
        self.description = None    # scrdesc
        self.datatypes = list()  # scrdatatypes
        self.dataformats = list()  # scrmimetypes
        self.iconName = None           # scricon
        self.version = None        # scrversion
        
        self._parse()
        
        if self.iconName is None:
            self.iconName = "lightning_bolt"
            
        if self.title is None:
            self.title = fileStorer.name
    
    def _parse(self):
        """ Parse the script and extract the meta data. """

        dataStream = self._fileStorer.readData()
        try:
            try:
                line = dataStream.readline()
                while line:
                    line = line.strip()
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
                    line = dataStream.readline()
            finally:
                dataStream.close()
        except IOError:
            raise ConfigurationError("Cannot read script data.")
    
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
            dataStream = self._fileStorer.readData()
        except PersistenceError, error:
            raise ConfigurationError("Cannot access script.\nReason: '%s'" % error.message)
        else:
            try:
                content = dataStream.read()
                content = content.replace("\r", "")
                exec(content, dict())
            except Exception, exc:
                for line in traceback.format_exception(sys.exc_info()[1], sys.exc_info()[0], sys.exc_info()[2]):
                    self._logger.debug(line)
                raise ConfigurationError("Script terminated with error-code '%s'." % str(exc))
            finally:
                dataStream.close()
                
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
                dataStream = self._baseDirFileStorer.getChild(constants.PREFERENCES_PAGE_MODULE_NAME).readData()
                content = dataStream.read()
                content = content.replace("\r", "")
                exec(content, dict())
            except Exception:
                for line in traceback.format_exception(sys.exc_info()[1], sys.exc_info()[0], sys.exc_info()[2]):
                    self._logger.debug(line)
                raise ConfigurationError("Unable to execute the preferences page of the script extension.")
            finally:
                dataStream.close()
       
         
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
