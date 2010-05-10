# pylint: disable-msg=C0103
#
# Created: 06.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: clean.py 3603 2008-12-01 13:26:31Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Target for cleaning of build results. 
"""


import os
import shutil
from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$LastChangedRevision: 3603 $"


class clean(Command):
    """ Cleans the build results. """
    
    description = "Cleans the build results."
    user_options = list()
    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.verbose = None
        Command.__init__(self, distribution)
        self.__buildConfiguration = BuildConfiguration()

    def initialize_options(self):
        """ Definition of command options. """
        
        self.verbose = False

    def finalize_options(self):
        """ Set final values of options. """
        
        self.verbose = self.distribution.verbose
        
    def run(self):
        """ Perform command actions. """

        self.__removeGeneratedGuiFiles()
        
        # Removing build directory
        if os.path.isdir(self.__buildConfiguration.buildDirectory):
            shutil.rmtree(self.__buildConfiguration.buildDirectory)
            if self.verbose:
                print("Removed build directory '%s'" % self.__buildConfiguration.buildDirectory)
        
        # Removing manifest files
        manifestTemplate = "MANIFEST.in" 
        if os.path.exists(manifestTemplate):
            os.remove(manifestTemplate)
            if self.verbose:
                print("Static image module '%s'" % manifestTemplate)
        manifest = "MANIFEST"
        if os.path.exists(manifest):
            os.remove(manifest)
            if self.verbose:
                print("Static image module '%s'" % manifest)

    def __removeGeneratedGuiFiles(self):
        """ Removes GUI-related generated files. """
        
        # Removing generated GUI modules
        for scriptExtension in self.__buildConfiguration.scriptExtensions.values():
            genGuiDir = scriptExtension.generatedPythonModuleDirectory
            if os.path.isdir(genGuiDir):
                shutil.rmtree(genGuiDir)
                if self.verbose:
                    print("Removed directory '%s'" % genGuiDir)
        if os.path.isdir(self.__buildConfiguration.generatedGuiModuleDirectory):
            shutil.rmtree(self.__buildConfiguration.generatedGuiModuleDirectory)
            if self.verbose:
                print("Removed directory '%s'" % self.__buildConfiguration.generatedGuiModuleDirectory)
                
        # Removing static images module
        if os.path.exists(self.__buildConfiguration.staticImageModulePath):
            os.remove(self.__buildConfiguration.staticImageModulePath)
            if self.verbose:
                print("Static image module '%s'" % self.__buildConfiguration.staticImageModulePath)
