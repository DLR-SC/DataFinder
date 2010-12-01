# pylint: disable=C0103
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
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
Implements the build target which generates required Qt4 resources.
"""


import os
import shutil

from distutils.cmd import Command

from datafinder_distutils import configuration
from datafinder_distutils.utils import regenerateFile


__version__ = "$Revision-Id:$" 


class _gen_qt4gui_modules(Command):
    """
    Implements command to generate python modules
    from Qt4 designer files.
    """

    description = "Generates Python modules from Qt designer files."
    user_options = [("pyuiccommand=",
                     None,
                     "Path and name of the pyuic command line tool."),
                     ("pyrcccommand=",
                     None,
                     "Path and name of the pyrcc command line tool."),
                     ("uidirectory=",
                     None,
                     "Path to the directory containing the ui files."),
                     ("ignoreuifilenames=",
                      None,
                      "List of ui files that have to be ignored.")]

    PYUIC_COMMAND_TEMPLATE = "%s -o %s %s"
    PYRCC_COMMAND_TEMPLATE = "%s -o %s %s"
    MESSAGE_SUCCESS_TEMPLATE = "Converted '%s' to '%s'."
    MESSAGE_FAILED_TEMPLATE = "Failed '%s' to '%s'."


    def __init__(self, distribution):
        """ Constructor. """

        self.__buildConfiguration = configuration.BuildConfiguration()
        self.pyuiccommand = None
        self.pyrcccommand = None
        self.uidirectory = None
        self.ignoreuifilenames = None
        self.uiTargetDirectory = self.__buildConfiguration.generatedGuiModuleDirectory
        self.basedirectory = None
        self.verbose = None
        Command.__init__(self, distribution)

    def initialize_options(self):
        """ Definition of command options. """

        self.pyuiccommand = "pyuic4"
        self.uidirectory = "resources/qt4/ui"
        self.ignoreuifilenames = ""
        self.basedirectory = "resources/qt4"
        self.defaultResourceFilePath = self.basedirectory + "/user_rc.py"
        self.verbose = False
        
    def finalize_options(self):
        """ Set final values of options. """

        self.ignoreuifilenames = self.ignoreuifilenames.split(";")
        self.verbose = self.distribution.verbose

    @staticmethod
    def _makePackage(packagePathName):
        """
        Create a new package at the given package path.

        @param packagePathName: Path of the new package.
        @type packagePathName: C{string}
        """

        if not os.path.exists(packagePathName):
            os.mkdir(packagePathName)
        initFileName = os.path.join(packagePathName, "__init__.py")
        open(initFileName, "w").close()

    def _convertUiFiles(self):
        """ Converting of the ui files to py files. """

        self._makePackage(self.uiTargetDirectory)
        for directoryName in os.listdir(self.uidirectory):
            directoryPath = os.path.join(self.uidirectory, directoryName)
            if os.path.isdir(directoryPath):
                packagePath = os.path.join(self.uiTargetDirectory, directoryName)
                self._makePackage(packagePath)  #Create python target package
                for fileName in os.listdir(directoryPath):
                    filePath = os.path.join(directoryPath, fileName)
                    if os.path.isfile(filePath) and fileName.endswith(".ui") and not fileName in self.ignoreuifilenames:
                        moduleName = fileName[:-3] + "_ui.py"
                        modulePath = os.path.join(packagePath, moduleName)
                        if regenerateFile(filePath, modulePath):
                            command = self.PYUIC_COMMAND_TEMPLATE % (self.pyuiccommand, modulePath, filePath)
                            msg = self.MESSAGE_FAILED_TEMPLATE
                            if os.system(command) == 0:
                                msg = self.MESSAGE_SUCCESS_TEMPLATE
                            if self.verbose:
                                print(msg % (filePath, moduleName))

    def _generateResourceFile(self):
        """ Generation of the image resource file. """

        if not os.path.exists(self.defaultResourceFilePath):
            directoryContent = os.listdir(self.basedirectory)
            for itemBaseName in directoryContent:
                itemName = os.path.join(self.basedirectory, itemBaseName)
                if os.path.isfile(itemName) and itemBaseName.endswith(".qrc"):
                    pythonDirectoryBaseName = itemBaseName[:-4]
                    pythonFileBaseName = pythonDirectoryBaseName + "_rc.py"
    
                    destinationPythonDirectoryName = os.path.join(self.uiTargetDirectory,
                                                                  pythonDirectoryBaseName)
                    if os.path.exists(destinationPythonDirectoryName):
                        destinationPythonFileName = os.path.join(destinationPythonDirectoryName,
                                                                 pythonFileBaseName)
                        command = self.PYRCC_COMMAND_TEMPLATE % (self.pyrcccommand,
                                                                 destinationPythonFileName,
                                                                 itemName)
    
                        msg = self.MESSAGE_FAILED_TEMPLATE
                        if os.system(command) == 0:
                            msg = self.MESSAGE_SUCCESS_TEMPLATE
                        if self.verbose:
                            print(msg % (itemBaseName, destinationPythonFileName))
                    else:
                        if self.verbose:
                            print("Unable to convert '%s'. Target '%s' doesn't exist." % (itemBaseName,
                                                                                          destinationPythonDirectoryName))
        else:
            targetDirectoryPath = os.path.join(self.uiTargetDirectory, "user")
            targetResourceFilePath = os.path.join(targetDirectoryPath, os.path.basename(self.defaultResourceFilePath))
            if regenerateFile(self.defaultResourceFilePath, targetResourceFilePath):
                print("Copying default resource file instead of generating it.")
                shutil.copy(self.defaultResourceFilePath, targetDirectoryPath)

    def run(self):
        """ Perform command actions. """

        self._convertUiFiles()
        self._generateResourceFile()
