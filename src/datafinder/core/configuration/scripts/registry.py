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
Implements a registry for script extensions.
"""


from copy import copy

from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration.scripts import constants
from datafinder.core.configuration.scripts.script import createScript
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import createFileStorer


__version__ = "$Revision-Id:$" 


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
        @type scripts: C{list} of C{Script} or C{ScriptCollection}
        """
        
        if not location in self._registeredScripts:
            self._registeredScripts[location] = dict()
        for script in scripts:
            self._registeredScripts[location][script.uri] = copy(script)
            if location == constants.LOCAL_SCRIPT_LOCATION:
                self._preferences.addScriptUri(script.uri)
            try:
                for script in script.scripts: 
                    if script.automatic:
                        script.execute()
            except AttributeError: #It is a script and not a collection                 
                if script.automatic:
                    script.execute()
                        
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
