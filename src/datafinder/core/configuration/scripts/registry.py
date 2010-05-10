#
# Created: 07.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: registry.py 4564 2010-03-25 22:30:55Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements a registry for script extensions.
"""


from copy import copy

from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration.scripts import constants
from datafinder.core.configuration.scripts.script import createScript
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import createFileStorer


__version__ = "$LastChangedRevision: 4564 $"


class ScriptRegistry(object):
    """ Global registry for script extensions. """
    
    _logger = getDefaultLogger()
    
    def __init__(self, preferences):
        """ 
        Constructor. 
        
        @param preferences: Global preferences object.
        @type preferences: L{PreferencesHandler<datafinder.core.configuration.preferences.PreferencesHandler>}
        """
        
        self._preferences = preferences
        self._registeredScripts = dict()

    @property
    def scripts(self):
        """ Getter for all existing scripts. """
        
        result = list()
        for locationScripts in self._registeredScripts.values():
            for script in locationScripts.values():
                result.append(copy(script))
        return result
    
    def load(self):
        """ 
        Loads local script extensions. 
        
        @raise ConfigurationError: Indicating problems on initialization.
        """

        scripts = list()
        for scriptUri in self._preferences.scriptUris:
            try:
                fileStorer = createFileStorer(scriptUri)
            except PersistenceError, error:
                self._logger.debug("Cannot access script '%s'. Reason '%s'" % (scriptUri, error.message))
            else:
                try:
                    script = createScript(fileStorer)
                except ConfigurationError, error:
                    self._logger.debug(error.message)
                else:
                    scripts.append(script)
        self._registeredScripts.clear()
        self.register(constants.LOCAL_SCRIPT_LOCATION, scripts)

    def getScripts(self, location):
        """ 
        Determines the scripts for the specific location. 
        
        @param location: Identifies the script location.
        @type location: C{unicode}
        
        @return: List of icons of the location.
        @rtype: C{list} of C{Script}
        """
        
        result = list()
        if location in self._registeredScripts:
            for script in self._registeredScripts[location].values():
                result.append(copy(script))
        return result
    
    def register(self, location, scripts):
        """ 
        Registers a script location. 
        
        @param location: Represents the scope / location of the icons.
        @type location: C{unicode}
        @param scripts: List of script that a registered.
        @type scripts: C{list} of C{Script}
        """
        
        if not location in self._registeredScripts:
            self._registeredScripts[location] = dict()
        for script in scripts:
            self._registeredScripts[location][script.uri] = copy(script)
            if location == constants.LOCAL_SCRIPT_LOCATION:
                self._preferences.addScriptUri(script.uri)

    def unregister(self, location, script):
        """ 
        Unregisters the given script.
        
        @param script: The script to unregister.
        @type script: C{Script}
        """
        
        if location in self._registeredScripts:
            if script.uri in self._registeredScripts[location]:
                del self._registeredScripts[location][script.uri]
                if location == constants.LOCAL_SCRIPT_LOCATION:
                    self._preferences.removeScriptUri(script.uri)

    def hasScript(self, location, scriptPath):
        """ Checks whether the specific icons exists. """
        
        return not self.getScript(location, scriptPath) is None
        
    def getScript(self, location, scriptUri):
        """ Returns the icon for the given location. """
        
        result = None
        if location in self._registeredScripts:
            if scriptUri in self._registeredScripts[location]:
                result = copy(self._registeredScripts[location][scriptUri])
        return result
