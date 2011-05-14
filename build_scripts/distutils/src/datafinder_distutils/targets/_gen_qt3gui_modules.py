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
Build Target for creation of Python modules from Qt3 designer files.
"""


import os
import shutil

from distutils.cmd import Command

from datafinder_distutils import configuration
from datafinder_distutils.utils import regenerateFile


__version__ = "$Revision-Id:$" 


_DEFAULT_STATIC_IMAGES_FILE_PATH = "resources/qt3/static_images.py"


class _gen_qt3gui_modules(Command):
    """ 
    Implements build target to generate Python modules from Qt3 designer files.
    """
    
    description = "Generates Python modules from Qt3 designer files."
    user_options = [("pyuiccommand=", 
                     None, 
                     "Path and name of the pyuic command line tool."),
                     ("uidirectory=", 
                     None, 
                     "Path to the Qt3-specific designer files.")]
        

    def __init__(self, distribution):
        """ Constructor. """
        
        self.__buildConfiguration = configuration.BuildConfiguration()
        self.pyuiccommand = None
        self.uidirectory = None
        self.verbose = None
        Command.__init__(self, distribution)

    def initialize_options(self):
        """ Definition of command options. """
        
        self.pyuiccommand = "pyuic"
        self.uidirectory = "resources/qt3/ui"
        self.verbose = False

    def finalize_options(self):
        """ Set final values of options. """
        
        self.verbose = self.distribution.verbose
    
    def run(self):
        """ Perform command actions. """
        
        destinationDirectory = self.__buildConfiguration.generatedGuiModuleDirectory
        self._createGeneratedUiPackage(destinationDirectory)
        self._generatePythonModulesFromUiFiles(self.uidirectory, destinationDirectory)
        
        self._generateResourceFile()

    @staticmethod
    def _createGeneratedUiPackage(destinationDirectory):
        """ Creates package for the generated Python modules. """
        
        if not (os.path.exists(destinationDirectory) and os.path.isdir(destinationDirectory)):
            os.mkdir(destinationDirectory)
        initModulePath = os.path.join(destinationDirectory, "__init__.py")
        if not (os.path.exists(initModulePath) and os.path.isfile(initModulePath)):
            fileHandle = open(initModulePath, "wb")
            fileHandle.write('""" Generated __init__.py file. """')
            fileHandle.close()

    def _generatePythonModulesFromUiFiles(self, uiDirectory, destinationDirectory):
        """ Converts all Qt designer files to according Python modules. """
        
        for sourceFileName in os.listdir(uiDirectory):
            sourceFilePath = os.path.join(uiDirectory, sourceFileName)
            if os.path.isfile(sourceFilePath) and sourceFileName.endswith(".ui"):
                pythonModuleName = sourceFileName[:-3] + ".py"
                targetFilePath = os.path.join(destinationDirectory, pythonModuleName)
                
                if regenerateFile(sourceFilePath, targetFilePath):
                    command = "%s -o %s %s" % (self.pyuiccommand, targetFilePath, sourceFilePath)
                    if os.system(command) == 0 and self.verbose:
                        print("Converted '%s' to '%s'." % (sourceFilePath, targetFilePath))

    def _generateResourceFile(self):
        """ Generates the image resource file. """
        
        targetDirectoryPath = self.__buildConfiguration.generatedGuiModuleDirectory
        imageFilePaths = ""
        if not os.path.exists(_DEFAULT_STATIC_IMAGES_FILE_PATH):
            for imageDirectory in [self.__buildConfiguration.imageDirectory, 
                                   self.__buildConfiguration.iconDirectory]:
                for imageName in os.listdir(imageDirectory):
                    if imageName.endswith(".png"):
                        imageFilePaths += os.path.join(imageDirectory, imageName) + " "
            command = self.pyuiccommand + " -embed DataFinder %s > %s" % (imageFilePaths, _DEFAULT_STATIC_IMAGES_FILE_PATH)
            if self.verbose:
                print(command)
            os.system(command)
        targetResourceFilePath = os.path.join(targetDirectoryPath, os.path.basename(_DEFAULT_STATIC_IMAGES_FILE_PATH))
        if regenerateFile(_DEFAULT_STATIC_IMAGES_FILE_PATH, targetResourceFilePath):
            print("Copying default static image file.")
            shutil.copy(_DEFAULT_STATIC_IMAGES_FILE_PATH, targetDirectoryPath)
