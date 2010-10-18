# pylint: disable-msg=C0103
#
# Created: 24.07.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: create_binary_distribution.py 4617 2010-04-18 11:08:49Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
This build target uses the bbfreeze module for creation of DataFinder distribution
including all required Python and C dependencies.
The distribution can be build on Linux and Windows operating systems. 
"""


import os
import sys
import shutil
from distutils.cmd import Command

from bbfreeze import Freezer

from datafinder_distutils.configuration import BuildConfiguration
from datafinder_distutils.utils import setVersion
 

__version__ = "$LastChangedRevision: 4617 $"


# some Python modules whose inclusion has to be forced
_forcedIncludes = ["datafinder", "sgmllib", "htmlentitydefs", 
                   "uuid", "unittest",
                   "ConfigParser", "Crypto.Util.randpool", "Crypto.PublicKey.DSA",
                   "Crypto.PublicKey.RSA", "Crypto.Cipher.Blowfish", "Crypto.Cipher.AES",
                   "Crypto.Hash.SHA", "Crypto.Hash.MD5", "Crypto.Hash.HMAC", 
                   "Crypto.Cipher.DES3", "Crypto.Util.number", "select",
				   "datafinder.persistence.adapters.filesystem.factory", 
				   "datafinder.persistence.adapters.webdav_.factory", 
				   "datafinder.persistence.adapters.tsm.factory",
                   "datafinder.persistence.adapters.archive.factory",
                   "datafinder.script_api.repository",
                   "datafinder.script_api.properties.property_support",
                   "datafinder.script_api.item.item_support"]
_win32ForcedIncludes = ["win32com", "win32com.client"]
_qtSpecificForcedIncludes = ["qt", "sip"]

_MANIFEST_FILE_CONTENT = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
    <noInheritable />
    <assemblyIdentity type="win32" name="Microsoft.VC90.CRT" version="9.0.30411.0" processorArchitecture="x86" />
    <file name="msvcr90.dll" /> 
    <file name="msvcp90.dll" /> 
    <file name="msvcm90.dll" />
</assembly>
"""
_DOCUMENTATION_DIRECTORY = "doc"


class bdist(Command):
    """ Creates a binary distribution containing all required C and Python extensions. """
    
    description = "Creates a platform-specific DataFinder distribution including all " + \
                  "required Python and C dependencies." 
    user_options = [("excludepythonshell", 
                     None, 
                     "Flag indicating the exclusion of the separate Python shell."),
                     ("outputformat=", 
                     None, 
                     "Format of the package format (nsis: NSIS installer (win32 only), " \
                     + "tar compressed tar archive). Default: No archive is created.")]
    sub_commands = [("gen", None), ("doc", None)]

    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.verbose = None
        self.generatemanifestfiles = None
        self.excludepythonshell = None
        self.outputformat = None
        
        self.__buildConfiguration = BuildConfiguration()
        self.destinationPath = os.path.join("./", 
                                            self.__buildConfiguration.buildDirectory,
                                            self.__buildConfiguration.fullName + "_" + sys.platform)
        Command.__init__(self, distribution)

    def initialize_options(self):
        """ Definition of command options. """
        
        self.excludepythonshell = False
        self.outputformat = None
        self.verbose = False
        
    def finalize_options(self):
        """ Set final values of options. """
        
        self.verbose = self.distribution.verbose
        self.excludepythonshell = bool(int(self.excludepythonshell))
        
    def run(self):
        """ Perform command actions. """

        # Preparation...        
        self._prepare()
        
        # Run sub commands
        for commandName in self.get_sub_commands():
            self.run_command(commandName)
        
        # Create the binary distribution
        from distutils import dist
        distutilDistributionClass = dist.Distribution # save reference to distutils Distribution class because it is overwritten by bbfreeze
        startScripts = [(scriptName, False) for scriptName in self.__buildConfiguration.getScripts()]
        self._createBinaryDistribution(startScripts)
        setattr(dist, "Distribution", distutilDistributionClass) # correct reference again so later build targets work properly
        
        if self.outputformat == "tar":
            self.run_command("_bdist_tar")
        elif self.outputformat == "nsis":
            self.run_command("_bdist_nsis")
        
    def _prepare(self):
        """ Prepares the source distribution creation. """
        
        epydocOptions = self.distribution.get_option_dict("doc")
        epydocOptions["destdir"] = ("", _DOCUMENTATION_DIRECTORY)
        modules = "src/datafinder/script_api"
        modules += ";src/datafinder/gui/user/script_api.py"
        epydocOptions["modules"] = ("", modules)

        setVersion(self.__buildConfiguration.fullName)

    def _createBinaryDistribution(self, startScripts):
        """ 
        Creates a binary DataFinder distribution for Linux/Windows platforms
        including the Python interpreter.
        
        @param startScripts: Contains a list of start scripts for which executables are generated. The scripts
                             are described by tuples of script path and a boolean indicating whether 
                             on the Windows platform a console window is visible or not.
        @type startScripts: C{list} of C{tuple} (C{unicode}/C{string}, C{bool})
        """
        
        forcedIncludes = _forcedIncludes[:]
        forcedIncludes.extend(_qtSpecificForcedIncludes)
        if sys.platform == "win32":
            forcedIncludes.extend(_win32ForcedIncludes)
        
        freezer = Freezer(self.destinationPath, includes=forcedIncludes)
        freezer.include_py = not self.excludepythonshell
        for scriptPath, guiOnly in startScripts:
            freezer.addScript(scriptPath, gui_only=guiOnly)
        
        # create distribution
        freezer()
        
        # copy readme, license, changes files
        shutil.copy(self.__buildConfiguration.readmeFile, self.destinationPath)
        shutil.copy(self.__buildConfiguration.licenseFile, self.destinationPath)
        shutil.copy(self.__buildConfiguration.changesFile, self.destinationPath)
        
        # copy image, example script files
        destinationImagePath = os.path.join(self.destinationPath, self.__buildConfiguration.imageDirectory)
        os.makedirs(destinationImagePath)
        baseImageDir = self.__buildConfiguration.imageDirectory
        for imageName in os.listdir(baseImageDir):
            if imageName.endswith(".ico"):
                shutil.copy(os.path.join(baseImageDir, imageName), destinationImagePath)
        
        scriptsExampleDir = self.__buildConfiguration.scriptExamplesDirectory
        shutil.copytree(scriptsExampleDir, os.path.join(self.destinationPath, scriptsExampleDir))
        scriptProjectDir = "script_extensions"
        shutil.copytree(scriptProjectDir, os.path.join(self.destinationPath, scriptProjectDir))
        docDir = "doc"
        shutil.copytree(docDir, os.path.join(self.destinationPath, docDir))
        shutil.rmtree(docDir)

        # create manifest files
        if sys.platform == "win32":
            scriptNames = [startScript[0] for startScript in startScripts]
            if not self.excludepythonshell:
                scriptNames.append("py.py")
            
            for scriptName in scriptNames:
                fileExtension = ".exe.manifest"
                content = _MANIFEST_FILE_CONTENT
                    
                fileBaseName = os.path.basename(scriptName).replace(".py", fileExtension)
                filePath = os.path.join(self.destinationPath, fileBaseName)
                fileHandle = open(filePath, "wb")
                fileHandle.write(content)
                fileHandle.close()
