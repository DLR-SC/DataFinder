# pylint: disable-msg=C0103
#
# Created: 30.07.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: generate_gui_modules.py 3603 2008-12-01 13:26:31Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Build Target for creation of Python modules from Qt designer files.
"""


import os

from distutils.cmd import Command

from datafinder_distutils import configuration


__version__ = "$LastChangedRevision: 3603 $"


class generate_gui_modules(Command):
    """ 
    Implements build target to generate Python modules from Qt designer files.
    """
    
    description = "Generates Python modules from Qt designer files."
    user_options = [("pyuiccommand=", 
                     None, 
                     "Path and name of the pyuic command line tool"),
                     ("projectname=", 
                     None, 
                     "Name of the project to create the GUI modules for.")]

    __pyuicCommandTemplate = "%s -o %s %s"
    
    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.__buildConfiguration = configuration.BuildConfiguration()
        self.pyuiccommand = None
        self.projectname = None
        self.verbose = None
        Command.__init__(self, distribution)

    def initialize_options(self):
        """ Definition of command options. """
        
        self.pyuiccommand = "pyuic"
        self.verbose = False

    def finalize_options(self):
        """ Set final values of options. """
        
        self.verbose = self.distribution.verbose
        if not self.projectname is None:
            if not self.projectname in self.__buildConfiguration.scriptExtensions:
                raise Exception("Project with name '%s' does not exist." % self.projectname)
    
    def run(self):
        """ Perform command actions. """
        
        if self.projectname is None:
            destinationDirectory = self.__buildConfiguration.generatedGuiModuleDirectory
            _createGeneratedUiPackage(destinationDirectory)
            self.__generatePythonModulesFromUiFiles(self.__buildConfiguration.qtDesignerDirectory, destinationDirectory)
            for scriptExtension in self.__buildConfiguration.scriptExtensions.values():
                uiDirectory = scriptExtension.qtDesignerDirectory
                destinationDirectory = scriptExtension.generatedPythonModuleDirectory
                _createGeneratedUiPackage(destinationDirectory)
                self.__generatePythonModulesFromUiFiles(uiDirectory, destinationDirectory)
        else:
            uiDirectory = self.__buildConfiguration.scriptExtensions[self.projectname].qtDesignerDirectory
            destinationDirectory = self.__buildConfiguration.scriptExtensions[self.projectname].generatedPythonModuleDirectory
            _createGeneratedUiPackage(destinationDirectory)
            self.__generatePythonModulesFromUiFiles(uiDirectory, destinationDirectory)

    def __generatePythonModulesFromUiFiles(self, uiDirectory, destinationDirectory):
        """ Converts all Qt designer files to according Python modules. """
        
        directoryContent = os.listdir(uiDirectory)
        for itemBaseName in directoryContent:
            itemName = os.path.join(uiDirectory, itemBaseName)
            if os.path.isfile(itemName) and itemBaseName.endswith(".ui"):
                pythonFileBaseName = itemBaseName[:-3] + ".py"
                destinationPythonFileName = os.path.join(destinationDirectory, pythonFileBaseName)
                command = self.__pyuicCommandTemplate % (self.pyuiccommand, destinationPythonFileName, itemName)
                if os.system(command) == 0 and self.verbose:
                    print("Converted '%s' to '%s'." % (itemName, destinationPythonFileName))


def _createGeneratedUiPackage(destinationDirectory):
    """ Creates package for the generated Python modules. """
    
    if not (os.path.exists(destinationDirectory) and os.path.isdir(destinationDirectory)):
        os.mkdir(destinationDirectory)
    initModulePath = os.path.join(destinationDirectory, "__init__.py")
    if not (os.path.exists(initModulePath) and os.path.isfile(initModulePath)):
        fileHandle = open(initModulePath, "wb")
        fileHandle.write('""" Generated __init__.py file. """')
        fileHandle.close()
