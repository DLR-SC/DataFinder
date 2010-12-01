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
Build Target for creation of Python modules from schemas for the configuration.
"""


import os
import sys

from distutils.cmd import Command

from datafinder_distutils import configuration
from datafinder_distutils.utils import regenerateFile


__version__ = "$Revision-Id:$" 


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
