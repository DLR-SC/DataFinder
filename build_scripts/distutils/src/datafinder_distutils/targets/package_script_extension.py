# pylint: disable-msg=C0103
#
# Created: 31.07.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: create_script_extension.py 4326 2009-11-09 12:15:28Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Build target for creation of script extensions.
"""


import os
from tarfile import TarFile

from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$LastChangedRevision: 4326 $"


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
