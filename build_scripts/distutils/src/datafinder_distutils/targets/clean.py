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

        # Removing build directory
        if os.path.isdir(self.__buildConfiguration.buildDirectory):
            shutil.rmtree(self.__buildConfiguration.buildDirectory)
            if self.verbose:
                print("Removed build directory '%s'" % self.__buildConfiguration.buildDirectory)

        # Removing generated GUI modules                
        if os.path.isdir(self.__buildConfiguration.generatedGuiModuleDirectory):
            shutil.rmtree(self.__buildConfiguration.generatedGuiModuleDirectory)
            if self.verbose:
                print("Removed generated GUI modules in directory '%s'" \
                      % self.__buildConfiguration.generatedGuiModuleDirectory)

        # Removing generated configuration modules
        if os.path.isdir(self.__buildConfiguration.generatedConfigurationDirectory):
            shutil.rmtree(self.__buildConfiguration.generatedConfigurationDirectory)
            if self.verbose:
                print("Removed generated configuration modules in directory '%s'" \
                      % self.__buildConfiguration.generatedConfigurationDirectory)
        
        # Removing manifest files
        manifestTemplate = "MANIFEST.in" 
        if os.path.exists(manifestTemplate):
            os.remove(manifestTemplate)
            if self.verbose:
                print("Removed manifest template '%s'" % manifestTemplate)
        manifest = "MANIFEST"
        if os.path.exists(manifest):
            os.remove(manifest)
            if self.verbose:
                print("Removed manifest '%s'" % manifest)
