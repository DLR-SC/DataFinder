#
# Created: 12.10.2010 schlauch <Tobias.Schlauch>
# Changed: $Id$ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Adapted sdist target
"""


import os 
import shutil
import sys

from distutils.command.sdist import sdist as sdist_

from datafinder_distutils.configuration import BuildConfiguration
from datafinder_distutils.utils import setVersion
        

__version__ = "$LastChangedRevision$"


_DOCUMENTATION_DIRECTORY = "doc"
_CONFIGURATION_FILE_NAME = "setup.cfg"
_EXCLUDE_CLIENTS_KEYWORD = "exclude-clients"
_REVISION_KEYWORD = "revision"
_IS_RELEASE_KEYWORD = "is_release"
_IGNORE_BUILD_TARGETS = ["clean.py", "bdist.py", "gen.py",
                         "doc.py", "_bdist_nsis.py",
                         "_bdist_tar.py", "_gen_configuration_modules.py", 
                         "_gen_qt3gui_modules.py", "_gen_qt4gui_modules.py", 
                         "_pylint.py", "audit.py",
                         "sdist.py", "doc.py", "gen.py"]


class sdist(sdist_):
    """ Adapted sdist target. """
    
    sub_commands = [("gen", None), ("doc", None)]


    def __init__(self, distribution):
        """ Constructor. """
        
        self.verbose = None
        sdist_.__init__(self, distribution)
        self.__buildConfiguration = BuildConfiguration()
        
        self.dist_dir = self.__buildConfiguration.distDirectory
    
    def run(self):
        """ 
        Sets some new configuration values and runs 
        the default run method of the sdist target.
        """

        # Adjust epydoc parameters, create manifest template, etc.
        self._prepare()
                
        # Run commands
        for commandName in self.get_sub_commands():
            self.run_command(commandName)
        self.distribution.packages = self.__buildConfiguration.getPackages() # Ensure that all packages are in
        self._createManifestTemplate()
        sdist_.run(self)
        
        # Clean up
        shutil.rmtree(_DOCUMENTATION_DIRECTORY)
        
    def _prepare(self):
        """ Prepares the source distribution creation. """
        
        epydocOptions = self.distribution.get_option_dict("doc")
        epydocOptions["destdir"] = ("", _DOCUMENTATION_DIRECTORY)
        modules = "src/datafinder/script_api"
        if not self.__buildConfiguration.excludeClients:
            modules += ";src/datafinder/gui/user/script_api.py"
        epydocOptions["modules"] = ("", modules)

        setVersion(self.__buildConfiguration.fullName)
        self._adjustSetupConfigurationFile()
        
    def _createManifestTemplate(self):
        """ Handles the creation of the manifest template file. """
        
        try:
            manifestFileObject = open("MANIFEST.in", "wb")
            for filePath in self._getAdditionalFiles():
                manifestFileObject.write("include %s\n" % filePath)
            for fileName in os.listdir(_DOCUMENTATION_DIRECTORY):
                manifestFileObject.write("include %s\n" % (os.path.join(_DOCUMENTATION_DIRECTORY, 
                                                                        fileName)))
            manifestFileObject.close()
        except IOError:
            print("Cannot create manifest template file.")
            sys.exit(-1)
            
    def _getAdditionalFiles(self):
        """ Determines all files which should be distributed but not installed. """
        
        additionalFiles = [self.__buildConfiguration.changesFile, 
                           self.__buildConfiguration.licenseFile,
                           os.path.join("script_extensions", "README.txt")]
        topLevelDirectories = [self.__buildConfiguration.unittestDirectory, 
                               self.__buildConfiguration.distutilSourceDirectory, 
                               self.__buildConfiguration.scriptExamplesDirectory]
        for directory in topLevelDirectories:
            for rootPath, dirNames, fileNames in os.walk(directory):
                for fileName in fileNames:
                    if fileName.endswith(".py") and not fileName in _IGNORE_BUILD_TARGETS:
                        additionalFiles.append(os.path.join(rootPath, fileName))
                if self.__buildConfiguration.excludeClients and "gui" in dirNames:
                    dirNames.remove("gui")
        return additionalFiles 

    def _adjustSetupConfigurationFile(self):
        """ Corrects the exclude_clients parameter so 
        everything works on installation as expected. """
        
        configurationFileObject = open(_CONFIGURATION_FILE_NAME, "rb")
        lines = configurationFileObject.readlines()
        configurationFileObject.close()
        for line in lines:
            if _EXCLUDE_CLIENTS_KEYWORD in line:
                index =  lines.index(line)
                lines.remove(line)
                lines.insert(index, _EXCLUDE_CLIENTS_KEYWORD + "=" 
                             + str(int(self.__buildConfiguration.excludeClients)) + "\n")
            elif _REVISION_KEYWORD in line:
                index =  lines.index(line)
                lines.remove(line)
                lines.insert(index, _REVISION_KEYWORD + "=" 
                             + self.__buildConfiguration.revision + "\n")
            elif _IS_RELEASE_KEYWORD in line:
                index =  lines.index(line)
                lines.remove(line)
                lines.insert(index, _IS_RELEASE_KEYWORD + "=" 
                             + str(int(self.__buildConfiguration.isRelease)) + "\n")
        configurationFileObject = open(_CONFIGURATION_FILE_NAME, "wb")
        configurationFileObject.writelines(lines)
        configurationFileObject.close()
