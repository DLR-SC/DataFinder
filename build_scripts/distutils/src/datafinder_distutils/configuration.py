# pylint: disable-msg=C0103, R0902
#
# Created: 30.07.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: configuration.py 4617 2010-04-18 11:08:49Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder/
#


"""
Provides access to the global build configuration parameters.
"""


import os
import sys
from ConfigParser import ConfigParser

from distutils.sysconfig import get_python_lib


__version__ = "$LastChangedRevision: 4617 $"


_globalSection = "global"
_scriptExtensionSection = "script_extensions"
_listSeparator = ";"


class BuildConfiguration(object):
    """ Allows access to the general configuration parameters. """

    __sharedState = {}

    def __init__(self, configurationFilePath=""):
        """
        Constructor.

        @param configurationFilePath: Path to the configuration file.
        @type configurationFilePath: C{unicode}/C{string}
        """

        self.__dict__ = self.__sharedState
        if len(self.__sharedState) <= 0:
            configParser = ConfigParser()
            configParser.read(configurationFilePath)

            self.includeClients = bool(int(configParser.get(_globalSection, "include_clients")))
            self.name = configParser.get(_globalSection, "name")
            self.author = configParser.get(_globalSection, "author")
            self.authorEmail = configParser.get(_globalSection, "author_email")
            self.maintainer = configParser.get(_globalSection, "maintainer")
            self.maintainerEmail = configParser.get(_globalSection, "maintainer_email")
            self.url = configParser.get(_globalSection, "url")
            self.version = configParser.get(_globalSection, "version")
            self.revision = os.environ.get("SVN_REVISION") or configParser.get(_globalSection, "revision")
            if os.environ.get("RELEASE_VERSION") is None:
                self.fullVersion = self.version + "-SNAPSHOT-" + self.revision
            else:
                self.fullVersion = self.version + "-RELEASE-" + self.revision
            self.fullName = self.name + "-" + self.fullVersion
            self.licenseFile = configParser.get(_globalSection, "license_file")
            self.readmeFile = configParser.get(_globalSection, "readme_file")
            self.changesFile = configParser.get(_globalSection, "changes_file")

            # general package names, directories, start scripts
            self.buildDirectory = configParser.get(_globalSection, "build_directory")
            self.epydocResultDirectory = configParser.get(_globalSection, "epydoc_result_directory")
            self.pylintResultDirectory = configParser.get(_globalSection, "pylint_result_directory")
            self.distDirectory = configParser.get(_globalSection, "dist_directory")
            self.unittestResultDirectory = configParser.get(_globalSection, "unittest_result_directory")

            self.imageDirectory = configParser.get(_globalSection, "image_directory")
            self.imageInstallDirectory = os.path.join(get_python_lib(), self.imageDirectory)[(len(sys.prefix) + 1):]
            self.qtDesignerDirectory = configParser.get(_globalSection, "qt3_designer_directory")
            self.generatedGuiModuleDirectory = configParser.get(_globalSection, "generated_gui_module_directory")
            self.sourceDirectory = configParser.get(_globalSection, "source_directory")
            self.package = configParser.get(_globalSection, "package")
            self.libSourceDirectory = configParser.get(_globalSection, "lib_source_directory")
            self.distutilSourceDirectory = configParser.get(_globalSection, "distutil_source_directory")
            self.distutilTargetPackage = configParser.get(_globalSection, "distutil_target_package")
            self.userClientStartScript = configParser.get(_globalSection, "userclient_start_script")
            self.adminClientStartScript = configParser.get(_globalSection, "adminclient_start_script")
            self.unittestDirectory = os.path.join(os.curdir, configParser.get(_globalSection, "unittest_directory"))
            self.unittestPackageSuffix = configParser.get(_globalSection, "unittest_package_suffix")
            self.unittestPackagePath = os.path.join(self.unittestDirectory, self.package + self.unittestPackageSuffix)
            self.staticImageModulePath = configParser.get(_globalSection, "static_image_module_path")

            # script extensions
            self.__scriptExtensions = dict()
            self.baseDirectoryNames = configParser.get(_scriptExtensionSection, "base_directory_names").split(_listSeparator)
            self.scriptExtensions = self.__initScriptExtensions(configParser)

    def __initScriptExtensions(self, configParser):
        """ Initializes script extension specific information. """

        scriptExtensions = dict()
        sourceDirectoryName = configParser.get(_scriptExtensionSection, "source_directory_name")
        testDirectoryName = configParser.get(_scriptExtensionSection, "test_directory_name")
        qtDesignerDirectoryName = configParser.get(_scriptExtensionSection, "qt_designer_directory_name")
        generatedGuiModuleDirectoryName = configParser.get(_scriptExtensionSection, "generated_gui_module_directory_name")

        for baseDirectoryName in self.baseDirectoryNames:
            baseConfig = ScriptExtensionBaseConfiguration(baseDirectoryName,
                                                          sourceDirectoryName,
                                                          testDirectoryName,
                                                          qtDesignerDirectoryName,
                                                          generatedGuiModuleDirectoryName,
                                                          self.unittestPackageSuffix)

            if os.path.isdir(baseDirectoryName):
                for directoryName in os.listdir(baseDirectoryName):
                    directoryPath = os.path.join(baseDirectoryName, directoryName)
                    if not directoryName.startswith(".") and os.path.isdir(directoryPath):
                        projectSourceDirectory = os.path.join(directoryPath, sourceDirectoryName)
                        packageName = None
                        for name in os.listdir(projectSourceDirectory):
                            if not name.startswith("."):
                                packageName = name
                                break
                        if not packageName is None:
                            scriptExtensions[directoryName] = ScriptExtensionConfiguration(directoryName, packageName, baseConfig)
        return scriptExtensions

    def getModules(self):
        """ Returns the list of Python modules. """

        if self.includeClients:
            return [self.userClientStartScript[:-3], self.adminClientStartScript[:-3]] # removing .py
        else:
            return list()

    def getAllPackages(self):
        """ Returns a list of all relevant packages. """

        if not self.includeClients:
            ignorePackageList = ["gui"]
        else:
            ignorePackageList = list()
        topLevelDirectoryList = [self.sourceDirectory, self.libSourceDirectory, self.distutilSourceDirectory]
        packageList = list()
        for directory in topLevelDirectoryList:
            for walkTuple in os.walk(directory):
                if "__init__.py" in walkTuple[2]: # directory is a python package
                    ignorePackage = False
                    for ignoredPackageName in ignorePackageList:
                        if ignoredPackageName in walkTuple[0]:
                            ignorePackage = True
                            break
                    if not ignorePackage:
                        packageList.append(walkTuple[0])
        return packageList


class ScriptExtensionBaseConfiguration(object):
    """ Contains base configuration parameters. """

    def __init__(self, baseDirectoryName, sourceDirectoryName, testDirectoryName,
                 qtDesignerDirectoryName, generatedGuiModuleDirectoryName,
                 unittestPackageNameSuffix):
        """ Initializes the base parameters. """

        self.baseDirectoryName = baseDirectoryName
        self.sourceDirectoryName = sourceDirectoryName
        self.testDirectoryName = testDirectoryName
        self.qtDesignerDirectoryName = qtDesignerDirectoryName
        self.generatedGuiModuleDirectoryName = generatedGuiModuleDirectoryName
        self.unittestPackageNameSuffix = unittestPackageNameSuffix


class ScriptExtensionConfiguration(object):
    """ Holds the configuration information of a script extension. """


    def __init__(self, name, packageName, baseConfiguration):
        """ Constructor. """

        self.name = name
        self.packageName = packageName
        self.__baseConfiguration = baseConfiguration
        self.baseDirectory = os.path.join(self.__baseConfiguration.baseDirectoryName, self.name)

    def __getQtDesignerDirectory(self):
        """ Returns the directory path of the Qt designer file directory. """

        return os.path.join(self.baseDirectory, self.__baseConfiguration.qtDesignerDirectoryName)

    qtDesignerDirectory = property(__getQtDesignerDirectory)

    def __getGeneratedPythonModuleDirectory(self):
        """ Returns the destination directory for the generated Python modules. """

        return os.path.join(self.sourceDirectory, self.packageName,
                            self.__baseConfiguration.generatedGuiModuleDirectoryName)

    generatedPythonModuleDirectory = property(__getGeneratedPythonModuleDirectory)

    def __getSourceDirectory(self):
        """ Returns the directory containing the script extension source code. """

        return os.path.join(self.baseDirectory, self.__baseConfiguration.sourceDirectoryName)

    sourceDirectory = property(__getSourceDirectory)

    def __getTestDirectory(self):
        """ Returns the directory containing script extension test code. """

        return os.path.join(self.baseDirectory, self.__baseConfiguration.testDirectoryName)

    testDirectory = property(__getTestDirectory)

    def __getTestPackageDirectory(self):
        """ Returns the directory identifying the test package. """

        return os.path.join(self.testDirectory, self.packageName + self.__baseConfiguration.unittestPackageNameSuffix)

    testPackageDirectory = property(__getTestPackageDirectory)
