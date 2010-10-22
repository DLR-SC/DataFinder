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
from ConfigParser import ConfigParser


__version__ = "$LastChangedRevision: 4617 $"


_GLOBAL_SECTION_KEYWORD = "global"
_SCRIPT_EXTENSION_SECTION_KEYWORD = "script_extensions"
_LIST_SEPARATOR = ";"
_SCRIPTAPI_DISTNAME_SUFFIX = "-Scripting-API"
        

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
            
            self._dist = None # distutils distribution information
            self.excludeClients = False
            
            self.name = configParser.get(_GLOBAL_SECTION_KEYWORD, "name")
            self.author = configParser.get(_GLOBAL_SECTION_KEYWORD, "author")
            self.authorEmail = configParser.get(_GLOBAL_SECTION_KEYWORD, "author_email")
            self.maintainer = configParser.get(_GLOBAL_SECTION_KEYWORD, "maintainer")
            self.maintainerEmail = configParser.get(_GLOBAL_SECTION_KEYWORD, "maintainer_email")
            self.url = configParser.get(_GLOBAL_SECTION_KEYWORD, "url")
            self.version = configParser.get(_GLOBAL_SECTION_KEYWORD, "version")
            self.revision = os.environ.get("SVN_REVISION") or configParser.get(_GLOBAL_SECTION_KEYWORD, "revision")
            if not os.environ.get("RELEASE_VERSION") is None:
                self.isRelease = True
            else:
                self.isRelease =  configParser.getboolean(_GLOBAL_SECTION_KEYWORD, "is_release")
            if not self.isRelease:
                self.fullVersion = self.version + "-SNAPSHOT-" + self.revision
            else:
                self.fullVersion = self.version + "-RELEASE-" + self.revision
            self.licenseFile = configParser.get(_GLOBAL_SECTION_KEYWORD, "license_file")
            self.readmeFile = configParser.get(_GLOBAL_SECTION_KEYWORD, "readme_file")
            self.changesFile = configParser.get(_GLOBAL_SECTION_KEYWORD, "changes_file")

            # general package names, directories, start scripts
            self.buildDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "build_directory")
            self.epydocResultDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "epydoc_result_directory")
            self.pylintResultDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "pylint_result_directory")
            self.distDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "dist_directory")
            self.unittestResultDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "unittest_result_directory")

            self.imageDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "image_directory")
            self.iconDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "icon_directory")
            self.generatedGuiModuleDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "generated_gui_module_directory")
            self.generatedConfigurationDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "generated_configuration_directory")
            self.sourceDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "source_directory")
            self.unittestDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "unittest_directory")
            self.scriptExamplesDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "script_examples_directory")
            self.distutilSourceDirectory = configParser.get(_GLOBAL_SECTION_KEYWORD, "distutil_source_directory")
            self.distutilTargetPackage = configParser.get(_GLOBAL_SECTION_KEYWORD, "distutil_target_package")
            self.distutilTargetPackagePath = os.path.join(self.distutilSourceDirectory, *(self.distutilTargetPackage.split(".")))
        
            self.userClientStartScript = configParser.get(_GLOBAL_SECTION_KEYWORD, "userclient_start_script")
            self.adminClientStartScript = configParser.get(_GLOBAL_SECTION_KEYWORD, "adminclient_start_script")
            
            # script extensions
            self.__scriptExtensions = dict()
            self.baseDirectoryNames = configParser.get(_SCRIPT_EXTENSION_SECTION_KEYWORD, "base_directory_names").split(_LIST_SEPARATOR)
            self.scriptExtensions = self.__initScriptExtensions(configParser)

    @property
    def fullName(self):
        """ Returns the name and the version information as string. """
        
        return self.name + "-" + self.fullVersion

    def __setDist(self, dist):
        """ Sets the distutils distribution information. """
        
        self._dist = dist
        self.excludeClients = bool(int(dist.exclude_clients))
        if self.excludeClients:
            self.name = self.name + _SCRIPTAPI_DISTNAME_SUFFIX
            
    dist = property(fset=__setDist)

    def __initScriptExtensions(self, configParser):
        """ Initializes script extension specific information. """

        scriptExtensions = dict()
        sourceDirectoryName = configParser.get(_SCRIPT_EXTENSION_SECTION_KEYWORD, "source_directory_name")
        testDirectoryName = configParser.get(_SCRIPT_EXTENSION_SECTION_KEYWORD, "test_directory_name")
        qtDesignerDirectoryName = configParser.get(_SCRIPT_EXTENSION_SECTION_KEYWORD, "qt_designer_directory_name")
        generatedGuiModuleDirectoryName = configParser.get(_SCRIPT_EXTENSION_SECTION_KEYWORD, "generated_gui_module_directory_name")

        for baseDirectoryName in self.baseDirectoryNames:
            baseConfig = ScriptExtensionBaseConfiguration(baseDirectoryName,
                                                          sourceDirectoryName,
                                                          testDirectoryName,
                                                          qtDesignerDirectoryName,
                                                          generatedGuiModuleDirectoryName)

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

    def getScripts(self):
        """ Returns the list of Python modules. """

        scripts = list()
        if not self.excludeClients:
            scripts.append(self.userClientStartScript)
            scripts.append(self.adminClientStartScript)
        return scripts

    def getPackages(self):
        """ Returns a list of all relevant packages. """

        if self.excludeClients:
            ignorePackageList = ["gui"]
        else:
            ignorePackageList = list()
        directory = self.sourceDirectory
        packages = list()
        for walkTuple in os.walk(directory):
            if "__init__.py" in walkTuple[2]: # directory is a python package
                ignorePackage = False
                for ignoredPackageName in ignorePackageList:
                    if ignoredPackageName in walkTuple[0]:
                        ignorePackage = True
                        break
                if not ignorePackage:
                    packages.append(walkTuple[0][(len(directory) + 1):])
        return packages


class ScriptExtensionBaseConfiguration(object):
    """ Contains base configuration parameters. """

    def __init__(self, baseDirectoryName, sourceDirectoryName, testDirectoryName,
                 qtDesignerDirectoryName, generatedGuiModuleDirectoryName):
        """ Initializes the base parameters. """

        self.baseDirectoryName = baseDirectoryName
        self.sourceDirectoryName = sourceDirectoryName
        self.testDirectoryName = testDirectoryName
        self.qtDesignerDirectoryName = qtDesignerDirectoryName
        self.generatedGuiModuleDirectoryName = generatedGuiModuleDirectoryName


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
