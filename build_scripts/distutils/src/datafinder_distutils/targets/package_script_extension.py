# pylint: disable=C0103
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
Build target for creation of script extensions.
"""


import os
from tarfile import TarFile

from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$Revision-Id:$" 


class package_script_extension(Command):
    """ Creates the plugin tar archive of a script extension. """
    
    description = "Creates the plugin tar archive."
    user_options = [("projectname=", 
                     None, 
                     "Name of the project to create the script extension for.")]
    sub_commands = [("_prepare", None)]
    
    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.__buildConfiguration = BuildConfiguration()
        self.verbose = None
        self.projectname = None
        Command.__init__(self, distribution)

    def initialize_options(self):
        """ Definition of command options. """
        
        self.verbose = False

    def finalize_options(self):
        """ Set final values of options. """
        
        self.verbose = self.distribution.verbose
        if not self.projectname is None:
            if not self.projectname in self.__buildConfiguration.scriptExtensions:
                raise Exception("Project with name '%s' does not exist." % self.projectname)
        
    def run(self):
        """ Perform command actions. """
        
        # Run commands
        for commandName in self.get_sub_commands():
            self.run_command(commandName)
        if self.projectname is None:
            if self.verbose:
                print("Create all known extensions.")
            for scriptExtension in self.__buildConfiguration.scriptExtensions.values():
                self._createScriptExtensionTarArchive(scriptExtension.baseDirectory, 
                                                      scriptExtension.packageName)
        else:
            scriptExtension = self.__buildConfiguration.scriptExtensions[self.projectname]
            self._createScriptExtensionTarArchive(scriptExtension.baseDirectory, 
                                                  scriptExtension.packageName)
            
    def _createScriptExtensionTarArchive(self, sourceDirectory, scriptExtensionName):
        """ Creates a TAR archive for the given script extension. """
        
        tarFileName = scriptExtensionName + ".tar"
        tarFilePath = os.path.join(self.__buildConfiguration.distDirectory, tarFileName)
        tarFile = TarFile(tarFilePath, "w")
        
        for inputDirectory in ["lib", "src"]:
            baseDirectory = os.path.join(sourceDirectory, inputDirectory)
            if os.path.exists(baseDirectory):
                for packageDirName in os.listdir(baseDirectory):
                    pythonModulesToAddList = list()
                    packageDirectory = os.path.join(baseDirectory, packageDirName)
                    if os.path.exists(packageDirectory):
                        for walkTuple in os.walk(packageDirectory):
                            directoryPath = walkTuple[0]
                            fileNameList = walkTuple[2]
                            for fileName in fileNameList:
                                if fileName.endswith(".py") or fileName == "SCRIPTS":
                                    filePath = os.path.join(directoryPath, fileName)
                                    pythonModulesToAddList.append(filePath)
            
                    for pythonModule in pythonModulesToAddList:
                        startPosition = pythonModule.find(baseDirectory) + len(baseDirectory) + 1
                        archiveName = pythonModule[startPosition:]
                        tarFile.add(pythonModule, archiveName)
        tarFile.close()
        if self.verbose:
            print("Created tar archive '%s'." % tarFilePath)
