# pylint: disable-msg=C0103, W0142
#
# Created: 27.06.2007 Tobias Schlauch <Tobias.Schlauch@dlr.de>
#
# Version: $Id: setup.py 4617 2010-04-18 11:08:49Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
# http://www.dlr.de/datafinder
# 


""" Setup script of the DataFinder project. """


__version__ = "$LastChangedRevision: 4617 $"


import os
import sys

from distutils import core
from distutils.dist import Distribution


Distribution.global_options.append(("exclude-clients", None, 
                                    "Excludes client-specific code."))


class Setup(object):
    """ Defines the setup process. """
    
    def __init__(self):
        """ Constructor. """
        
        self.__buildConfiguration = self._readConfiguration()
        self.__buildTargets = self._initBuildTargets()
        self.__buildConfiguration.dist = self._callSetup("commandline") # Initial call to get the configuration parameters
        
    @staticmethod
    def _readConfiguration():
        """ Adds DataFinder specific libraries to the Python path. """
        
        distutilsSourceDirectory = "build_scripts/distutils/src"
        sys.path.append(os.path.join(os.curdir, distutilsSourceDirectory))
        
        from datafinder_distutils.configuration import BuildConfiguration
        
        buildConfiguration = BuildConfiguration("setup.cfg")
        
        pythonPath = os.environ.get("PYTHONPATH")
        if pythonPath is None:
            pythonPath = ""
       
        # determine environment separator 
        separator = os.pathsep
        
        # adapt PYTHONPATH
        workingDirectory = os.curdir
        sourcePaths = list()
        sourcePaths.append(os.path.join(workingDirectory, buildConfiguration.sourceDirectory))
        sourcePaths.append(os.path.join(workingDirectory, buildConfiguration.unittestDirectory))
        
        # set environment variable PYTHONPATH
        # add paths to internal PYTHONPATH
        for path in sourcePaths:
            if not path in sys.path:
                sys.path.append(path)
            pythonPath += os.path.realpath(path) + separator
        os.environ["PYTHONPATH"] = pythonPath
        return buildConfiguration
    
    def _initBuildTargets(self):
        """ Imports and returns existing custom build targets. """
    
        buildTargets = dict()
        for buildTargetModule in os.listdir(self.__buildConfiguration.distutilTargetPackagePath):
            if not buildTargetModule == "__init__.py" and buildTargetModule.endswith(".py"):
                targetName = buildTargetModule[:-3]
                dottedClassName = self.__buildConfiguration.distutilTargetPackage + "." + targetName
                try:
                    moduleInstance = __import__(dottedClassName, globals(), locals(), [""])
                    classObject = getattr(moduleInstance, targetName)
                except (ImportError, AttributeError), error:
                    print("Cannot import '%s'\nReason: '%s'." % (dottedClassName, str(error.args)))
                else:
                    buildTargets[targetName] = classObject
        return buildTargets

    def _callSetup(self, stopBehavior=None):
        """ Actually runs the setup method and returns the distribution instance. """
        
        core._setup_stop_after = stopBehavior
        return core.setup(name=self.__buildConfiguration.name,
                          version=self.__buildConfiguration.fullVersion,
                          author = self.__buildConfiguration.author,
                          author_email = self.__buildConfiguration.authorEmail,
                          maintainer = self.__buildConfiguration.maintainer,
                          maintainer_email = self.__buildConfiguration.maintainerEmail,
                          url = self.__buildConfiguration.url,
                          cmdclass=self.__buildTargets,
                          package_dir = {"":"src"},
                          scripts = self.__buildConfiguration.getScripts(),
                          packages = self.__buildConfiguration.getPackages())
        
    def performSetup(self):
        """ Performs the different build targets. """
    
        self._callSetup()


Setup().performSetup()
