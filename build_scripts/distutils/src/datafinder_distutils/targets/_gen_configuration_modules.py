# pylint: disable-msg=C0103
#
# Created: 30.07.2008 wend_he <Heinrich.Wendel@dlr.de>
# Changed: $Id: generate_gui_modules.py 3603 2008-12-01 13:26:31Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Build Target for creation of Python modules from schemas for the configuration.
"""


import os
import sys

from distutils.cmd import Command

from datafinder_distutils import configuration
from datafinder_distutils.utils import regenerateFile


__version__ = "$LastChangedRevision: 3603 $"


_GENERATE_DS_DEFAULT_SCRIPT = "generateDS.py"


class _gen_configuration_modules(Command):
    """ 
    Implements build target to generate configuration modules from XML schema files.
    """
    
    description = "Generates configuration modules from XML schema files."
    
    user_options = [("generatedscommand=", 
                     None, 
                     "Path to the generateDS command."),
                     ("xsddirectory=", 
                     None,
                     "Directory of the schema files.")]

    __generatedDsCommandTemplate = "%s -f -m --silence --use-old-getter-setter --no-process-includes -o %s %s"
    
    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.__buildConfiguration = configuration.BuildConfiguration()
        self.generatedscommand = None
        self.xsddirectory = None
        self.verbose = None
        Command.__init__(self, distribution)

    def initialize_options(self):
        """ Set initial values. """
    
        self.generatedscommand = _GENERATE_DS_DEFAULT_SCRIPT
        self.xsddirectory = "resources/configuration"
    
    def finalize_options(self):
        """ Set final values of options. """
        
        self.verbose = self.distribution.verbose
    
    def run(self):
        """ Perform command actions. """
        
        self.makePackage(self.__buildConfiguration.generatedConfigurationDirectory)
        for fileName in os.listdir(self.xsddirectory):
            if fileName.endswith(".xsd"):
                moduleName = fileName.replace(".xsd", ".py")
                sourceFilePath = os.path.join(self.xsddirectory, fileName)
                targetFilePath = os.path.join(self.__buildConfiguration.generatedConfigurationDirectory, moduleName)
                if regenerateFile(sourceFilePath, targetFilePath):
                    # On win32 systems the direct call of a Python script make it "forget" its input parameters.
                    # Thus call it directly by the correct Python interpreter.
                    if sys.platform == "win32" and self.generatedscommand == _GENERATE_DS_DEFAULT_SCRIPT:
                        self.generatedscommand = os.path.join(os.path.normpath(sys.exec_prefix), "Scripts", self.generatedscommand)
                        self.generatedscommand = "%s %s" % (sys.executable, self.generatedscommand) 
                    command = self.__generatedDsCommandTemplate % (self.generatedscommand, targetFilePath, sourceFilePath)
                    
                    if self.verbose:
                        print(command)
                    if os.system(command) != 0:
                        print("Failed to generate configuration class from XSD schema for file: " + fileName)

    @staticmethod
    def makePackage(packagePathName):
        """
        Create a new package at the given package path.

        @param packagePathName: Path of the new package.
        @type packagePathName: C{string}
        """

        if not os.path.exists(packagePathName):
            os.mkdir(packagePathName)

        initFilePath = os.path.join(packagePathName, "__init__.py")
        if not os.path.exists(initFilePath):
            open(initFilePath, "wb").close()
