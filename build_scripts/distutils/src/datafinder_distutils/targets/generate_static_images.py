# pylint: disable-msg=C0103
# Created: 24.07.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: generate_static_images.py 4505 2010-03-04 14:22:02Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Runs the pyuic command and generate a Python 
module containing all image files.
"""


import os
from distutils.cmd import Command
import shutil

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$LastChangedRevision: 4505 $"


_DEFAULT_STATIC_IMAGES_FILE_PATH = "resources/qt3/static_images.py"


class generate_static_images(Command):
    """ Runs the pyuic command and generate a Python module containing all image files. """
    
    description = "Generates Python modules from Qt designer files."
    user_options = [("pyuiccommand=", 
                     None, 
                     "Path and name of the pyuic command line tool")]
    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.verbose = None
        self.pyuiccommand = None
        Command.__init__(self, distribution)
        self.__buildConfiguration = BuildConfiguration()

    def initialize_options(self):
        """ Definition of command options. """
        
        self.verbose = False
        self.pyuiccommand = "pyuic"

    def finalize_options(self):
        """ Set final values of options. """
        
        self.verbose = self.distribution.verbose
        
    def run(self):
        """ Perform command actions. """
        
        imageBaseDir = self.__buildConfiguration.imageDirectory
        destinationPath = self.__buildConfiguration.staticImageModulePath
        imageFilePaths = ""
        if not os.path.exists(_DEFAULT_STATIC_IMAGES_FILE_PATH):
            for imageName in os.listdir(imageBaseDir):
                if imageName.endswith(".png"):
                    imageFilePaths += os.path.join(imageBaseDir, imageName) + " "
            pyuicCommand = self.pyuiccommand + " -embed DataFinder %s > %s" % (imageFilePaths, destinationPath)
            if self.verbose:
                print(pyuicCommand)
            os.system(pyuicCommand)
        else:
            print "Copying default static image file instead of generating it."
            shutil.copy(_DEFAULT_STATIC_IMAGES_FILE_PATH, destinationPath)
