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


""" Setup script for the DataFinder project. """


__version__ = "$LastChangedRevision: 4617 $"


import os
import sys

from distutils.core import setup
from distutils.sysconfig import get_python_lib


def performSetup():
    """  Performs the different build targets. """
    
    buildConfiguration = _readConfiguration()
    _createBuildDirectories(buildConfiguration)
    _decorateSdistTarget(buildConfiguration.fullName, buildConfiguration.distDirectory)
    _createManifestTemplate(buildConfiguration.licenseFile, buildConfiguration.changesFile)
    buildTargets = _initBuildTargets(buildConfiguration) 
    
    setup(name=buildConfiguration.name,
          version=buildConfiguration.fullVersion,
          author = buildConfiguration.author,
          author_email = buildConfiguration.authorEmail,
          maintainer = buildConfiguration.maintainer,
          maintainer_email = buildConfiguration.maintainerEmail,
          url = buildConfiguration.url,
          cmdclass=buildTargets,
          py_modules = buildConfiguration.getModules(),
          packages = buildConfiguration.getAllPackages())


def _createManifestTemplate(licenseFile, changesFile):
    """ Handles the creation of the manifest template file. """
    
    manifestTemplateFileName = "MANIFEST.in"
    if not os.path.exists(manifestTemplateFileName):
        try:
            fileHandle = open(manifestTemplateFileName, "wb")
            fileHandle.write("include %s" % licenseFile)
            fileHandle.write("include %s" % changesFile)
            fileHandle.close()
        except IOError:
            print("Cannot create manifest template file.")
            sys.exit(-1)

                
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
    sourcePaths.append(os.path.join(workingDirectory, buildConfiguration.libSourceDirectory))
    sourcePaths.append(os.path.join(workingDirectory, buildConfiguration.unittestDirectory))
    for scriptExtension in buildConfiguration.scriptExtensions.values():
        scriptExtensionSourcePath = os.path.join(workingDirectory, scriptExtension.sourceDirectory)
        sourcePaths.append(scriptExtensionSourcePath)
        scriptExtensionTestPath = os.path.join(workingDirectory, scriptExtension.testDirectory)
        sourcePaths.append(scriptExtensionTestPath)
    
    # set environment variable PYTHONPATH
    # add paths to internal PYTHONPATH
    for path in sourcePaths:
        if not path in sys.path:
            sys.path.append(path)
        pythonPath += os.path.realpath(path) + separator
    # explicitly adding the site-packages location, required for pylint
    pythonPath += get_python_lib() + separator
    os.environ["PYTHONPATH"] = pythonPath
    return buildConfiguration


def _createBuildDirectories(buildConfiguration):
    """ Creates directories for the build artifacts. """
    
    if not os.path.isdir(buildConfiguration.buildDirectory):
        os.mkdir(buildConfiguration.buildDirectory)
    if not os.path.isdir(buildConfiguration.epydocResultDirectory):
        os.mkdir(buildConfiguration.epydocResultDirectory)
    if not os.path.isdir(buildConfiguration.pylintResultDirectory):
        os.mkdir(buildConfiguration.pylintResultDirectory)
    if not os.path.isdir(buildConfiguration.distDirectory):
        os.mkdir(buildConfiguration.distDirectory)
    if not os.path.isdir(buildConfiguration.unittestResultDirectory):
        os.mkdir(buildConfiguration.unittestResultDirectory)


def _decorateSdistTarget(versionString, distributionDirectory):
    """ 
    Decorates the method C{run} of the class L{distutils.command.sdist.sdist}
    with the functionality of setting the correct version number before building
    the source package.
    """
    
    from distutils.command.sdist import sdist
    from datafinder_distutils.utils import setVersion
    
    runMethod = sdist.run
    def decoratedRunMethod(self):
        setVersion(versionString)
        self.dist_dir = distributionDirectory
        runMethod(self)
    sdist.run = decoratedRunMethod


def _initBuildTargets(buildConfiguration):
    """ Imports and returns existing custom build targets. """
    
    buildTargets = dict()
    dottedTargetPackage = buildConfiguration.distutilTargetPackage
    targetPackageParts = dottedTargetPackage.split(".")
    targetPackagePath = os.path.join(buildConfiguration.distutilSourceDirectory, *targetPackageParts)
    for buildTargetModule in os.listdir(targetPackagePath):
        if not buildTargetModule == "__init__.py" and buildTargetModule.endswith(".py"):
            targetName = buildTargetModule[:-3]
            dottedClassName = dottedTargetPackage + "." + targetName
            try:
                moduleInstance = __import__(dottedClassName, globals(), locals(), [""])
                classObject = getattr(moduleInstance, targetName)
            except (ImportError, AttributeError):
                print ("Cannot import '%s'." % dottedClassName)
            else:
                buildTargets[targetName] = classObject
    return buildTargets


performSetup()
