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
import shutil


"""
Implements the build target which generates required Qt4 resources.
"""


import os

from distutils.cmd import Command

from datafinder_distutils import configuration


__version__ = "$LastChangedRevision: 4392 $"


class generate_qt4_resources(Command):
    """
    Implements command to generate python modules
    from Qt designer files.
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
        """
        Converting of the ui files to py files.
        """

        print("Convert *.ui to *.py files...")
        self._makePackage(self.uiTargetDirectory)
        directoryList = os.listdir(self.uidirectory)
        for directoryBaseName in directoryList:
            directoryName = os.path.join(self.uidirectory, directoryBaseName)
            if os.path.isdir(directoryName):
                directoryContent = os.listdir(directoryName)
                for itemBaseName in directoryContent:
                    itemPath = os.path.join(directoryName, itemBaseName)
                    if os.path.isfile(itemPath) and itemBaseName.endswith(".ui") and not itemBaseName in self.ignoreuifilenames:
                        pythonFileBaseName = itemBaseName[:-3] + "_ui.py"
                        destinationPythonDirectoryName = os.path.join(self.uiTargetDirectory,
                                                                      directoryBaseName)
                        #Create python package
                        self._makePackage(destinationPythonDirectoryName)

                        destinationPythonFileName = os.path.join(destinationPythonDirectoryName,
                                                                 pythonFileBaseName)
                        command = self.PYUIC_COMMAND_TEMPLATE % (self.pyuiccommand,
                                                                 destinationPythonFileName,
                                                                 itemPath)

                        msg = self.MESSAGE_FAILED_TEMPLATE
                        if os.system(command) == 0:
                            msg = self.MESSAGE_SUCCESS_TEMPLATE
                        if self.verbose:
                            print msg % (itemBaseName, pythonFileBaseName)

    def _generateResourceFile(self):
        """
        Generation of the resource_rc.py file.
        """

        print("Generating resource file...")
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
                            print msg % (itemBaseName, destinationPythonFileName)
                    else:
                        if self.verbose:
                            print("Unable to convert '%s'. Target '%s' doesn't exist." % (itemBaseName,
                                                                                          destinationPythonDirectoryName))
        else:
            print("Copying default resource file instead of generating it.")
            shutil.copy(self.defaultResourceFilePath, self.uiTargetDirectory + "/user")

    def run(self):
        """
        Perform command actions.
        """

        self._convertUiFiles()
        self._generateResourceFile()
