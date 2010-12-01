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
Target for cleaning of build results. 
"""


import os
import shutil
from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$Revision-Id:$" 


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
