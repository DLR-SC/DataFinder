# pylint: disable-msg=C0103
#
# Created: 06.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: generate_qt4_resources.py 4392 2010-01-15 11:55:33Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
# http://www.dlr.de/datafinder/
#


"""
Implements the build target which generates required Qt4 resources.
"""


import os
import shutil

from distutils.cmd import Command

from datafinder_distutils import configuration
from datafinder_distutils.utils import regenerateFile


__version__ = "$LastChangedRevision: 4392 $"


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
