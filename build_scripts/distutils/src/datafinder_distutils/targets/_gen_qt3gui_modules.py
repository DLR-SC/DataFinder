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
Build Target for creation of Python modules from Qt3 designer files.
"""


import os
import shutil

from distutils.cmd import Command

from datafinder_distutils import configuration
from datafinder_distutils.utils import regenerateFile


__version__ = "$LastChangedRevision: 3603 $"


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
            command = self.pyuiccommand + " -embed DataFinder %s > %s" % (imageFilePaths, targetDirectoryPath)
            if self.verbose:
                print(command)
            os.system(command)
        else:
            targetResourceFilePath = os.path.join(targetDirectoryPath, os.path.basename(_DEFAULT_STATIC_IMAGES_FILE_PATH))
            if regenerateFile(_DEFAULT_STATIC_IMAGES_FILE_PATH, targetResourceFilePath):
                print("Copying default static image file instead of generating it.")
                shutil.copy(_DEFAULT_STATIC_IMAGES_FILE_PATH, targetDirectoryPath)
