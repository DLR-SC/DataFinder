#
# Created: 07.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: handler.py 4572 2010-03-28 22:57:29Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the handling of script extensions of a specific repository.
"""


from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration.scripts.script import createScript
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import createFileStorer
from datafinder.persistence.metadata.constants import MODIFICATION_DATETIME


__version__ = "$LastChangedRevision: 4572 $"


class ScriptHandler(object):
    """
    Handles scripts of a specific repository.
    """
    
    __logger = getDefaultLogger()

    def __init__(self, scriptRegistry, sourceFileStorer, targetFileStorer):
        """
        Constructor.
        
        @param scriptRegistry: Global registry for scripts.
        @type scriptRegistry: L{ScriptRegistry<datafinder.core.configuration.scripts.registry.ScriptRegistry>}
        @param sourceFileStorer: Represents the source directory containing scripts.
        @type sourceFileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        @param targetFileStorer: Represents the target directory of the scripts.
        @type targetFileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        """

        self._scriptRegistry = scriptRegistry
        self._location = targetFileStorer.identifier
        self._sourceFileStorer = sourceFileStorer
        self._targetFileStorer = targetFileStorer
    
    @property    
    def allScripts(self):
        """ Getter for all defined scripts. """
        
        return self._scriptRegistry.scripts

    @property
    def scripts(self):
        """ Getter for handler-specific scripts. """
        
        return self._scriptRegistry.getScripts(self._location)
        
    def load(self):
        """
        Loads the scripts in the target directory and registers corresponding scripts.
        
        @raise ConfigurationError: Indicating problems.
        """

        self.__logger.info("Loading scripts...")
        try:
            if not self._targetFileStorer.exists():
                self._targetFileStorer.createCollection(True)
        except PersistenceError, error:
            raise ConfigurationError("Cannot access target location of repository-specific " \
                                     + "script extensions.\nReason: '%s'" % error.message)
        else:
            numberOfDownloadedScripts = 0
            try:
                children = self._sourceFileStorer.getChildren()
            except PersistenceError, error:
                raise ConfigurationError("Cannot retrieve icons. Reason: '%s'" % error.message)
            else:
                for source in children:
                    target = self._targetFileStorer.getChild(source.name)
                    updateRequired = self._isUpdateRequired(source, target)
                    if updateRequired:
                        try:
                            self._copy(source, target)
                            numberOfDownloadedScripts += 1
                        except PersistenceError, error:
                            self.__logger.error("Cannot retrieve script file '%s'. Reason '%s'" % (source.name, error.message))
                self._registerScripts()
                if numberOfDownloadedScripts > 0:
                    self.__logger.info("Retrieved %i script extensions." % numberOfDownloadedScripts)
    
    def _registerScripts(self):
        """ Registers all retrieved scripts. """
        
        scripts = list()
        try:
            children = self._targetFileStorer.getChildren()
        except PersistenceError, error:
            raise ConfigurationError("Cannot register repository-specific script extensions.\nReason: '%s'" % error.message)
        else:
            for fileStorer in children:
                try:
                    script = createScript(fileStorer, self._location)
                except ConfigurationError, error:
                    self.__logger.debug(error.message)
                else:
                    scripts.append(script)
            self._scriptRegistry.register(self._location, scripts)
            
    @staticmethod
    def _isUpdateRequired(source, target):
        """ Checks whether an update of an existing script extension is required. """
        
        updateRequired = False
        try:
            sourceModificationDatetime = source.retrieveMetadata([MODIFICATION_DATETIME])[MODIFICATION_DATETIME].value
            targetModificationDatetime = target.retrieveMetadata([MODIFICATION_DATETIME])[MODIFICATION_DATETIME].value
            if sourceModificationDatetime > targetModificationDatetime:
                updateRequired = True
        except PersistenceError:
            updateRequired = True
        return updateRequired
            
    def create(self):
        """ Creates directory for script extensions. """
    
        try:
            self._sourceFileStorer.createCollection()
        except PersistenceError, error:
            raise ConfigurationError("Cannot create script extensions collection. Reason: '%s'" % error.message)
    
    def getScript(self, localScriptPathName):
        """
        Returns a script for the given script file base name or C{None}.
        
        @param localScriptPathName: Base name of the local script extension file.
        @type localScriptPathName: C{unicode}
        
        @return: The script or C{None}.
        @rtype: C{Script}
        """
        
        targetStorer = self._targetFileStorer.getChild(localScriptPathName)
        return self._scriptRegistry.getScript(self._location, targetStorer.uri)

    def addScript(self, scriptUri):
        """
        Adds a new script.

        @param scriptUri: URI identifying the new script extension.
        @type scriptUri: C{unicode}
        
        @raise ConfigurationError: Indicating problems on icon importing.
        """

        try:
            scriptFileStorer = createFileStorer(scriptUri)
            if not scriptFileStorer.exists():
                raise ConfigurationError("The script '%s' cannot be found." % scriptUri)
            script = createScript(scriptFileStorer)
            for scriptDestination in [self._sourceFileStorer, self._targetFileStorer]:
                scriptDestinationFileStorer = scriptDestination.getChild(scriptFileStorer.name)
                self._copy(scriptFileStorer, scriptDestinationFileStorer)
            script = createScript(self._targetFileStorer.getChild(scriptFileStorer.name), self._location)
            self._scriptRegistry.register(self._location, [script])
        except PersistenceError, error:
            raise ConfigurationError("Cannot add script '%s'. Reason: '%s'" % (scriptUri, error.message))
    
    @staticmethod
    def _copy(source, destination):
        """ Transfers data from source to destination. """
        
        if not destination.exists():
            destination.createResource()
        fileObj = source.readData()
        destination.writeData(fileObj)
                
    def removeScript(self, script):
        """
        Removes a script.

        @param script: Script to remove.
        @type script: C{Script}
        """

        try:
            targetScriptFileStorer = self._targetFileStorer.getChild(script.name)
            if targetScriptFileStorer.exists():
                targetScriptFileStorer.delete()
                
            self._scriptRegistry.unregister(self._location, script)
            
            sourceScriptFileStorer = self._sourceFileStorer.getChild(script.name)
            if sourceScriptFileStorer.exists():
                sourceScriptFileStorer.delete()
        except PersistenceError, error:
            raise ConfigurationError("Cannot remove script extension '%s'.\nReason: '%s'" % (script.name, error.message))
        
    def hasScript(self, localScriptPathName):
        """ 
        Checks whether the specific script is already imported. 
        
        @param localScriptPathName: Base name of the local script extension file.
        @type localScriptPathName: C{unicode}
        
        @return: Flag indicating existence.
        @rtype: C{bool}
        """
        
        targetStorer = self._targetFileStorer.getChild(localScriptPathName)
        return self._scriptRegistry.hasScript(self._location, targetStorer.uri)
