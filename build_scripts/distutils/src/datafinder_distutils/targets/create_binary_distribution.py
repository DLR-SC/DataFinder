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
                   "qt", "sip",
                   "ConfigParser", "Crypto.Util.randpool", "Crypto.PublicKey.DSA",
                   "Crypto.PublicKey.RSA", "Crypto.Cipher.Blowfish", "Crypto.Cipher.AES",
                   "Crypto.Hash.SHA", "Crypto.Hash.MD5", "Crypto.Hash.HMAC", 
                   "Crypto.Cipher.DES3", "Crypto.Util.number", "select",
                   "unittest", 
				   "datafinder.persistence.adapters.filesystem.factory", 
				   "datafinder.persistence.adapters.webdav_.factory", 
				   "datafinder.persistence.adapters.tsm.factory",
                   "datafinder.persistence.adapters.archive.factory",
                   "datafinder.script_api.repository",
                   "datafinder.script_api.properties.property_support",
                   "datafinder.script_api.item.item_support"]
_win32ForcedIncludes = ["win32com", "win32com.client"]


class create_binary_distribution(Command):
    """ Creates a binary distribution containing all required C and Python extensions. """
    
    description = "Creates a platform-specific DataFinder distribution including all " + \
                  "required Python and C dependencies." 
    user_options = [("excludepythonshell", 
                     None, 
                     "Flag indicating the exclusion of the separate Python shell."),
                     ]
    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.verbose = None
        self.excludepythonshell = None
        
        self.__buildConfiguration = BuildConfiguration()
        self.destinationPath = os.path.join("./", 
                                            self.__buildConfiguration.buildDirectory,
                                            self.__buildConfiguration.fullName + "_" + sys.platform)
        Command.__init__(self, distribution)

    def initialize_options(self):
        """ Definition of command options. """
        
        self.excludepythonshell = True
        self.verbose = False
        
    def finalize_options(self):
        """ Set final values of options. """
        
        self.verbose = self.distribution.verbose
        self.excludepythonshell = bool(int(self.excludepythonshell))
        
    def run(self):
        """ Perform command actions. """
        
        setVersion(self.__buildConfiguration.fullName)
        startScripts = list()
        if self.__buildConfiguration.includeClients:
            startScripts.append((self.__buildConfiguration.userClientStartScript, False))
            startScripts.append((self.__buildConfiguration.adminClientStartScript, False))
        
        from distutils import dist
        distutilDistributionClass = dist.Distribution # save reference to distutils Distribution class because it is overwritten by bbfreeze
        self.__createBinaryDistribution(startScripts)
        setattr(dist, "Distribution", distutilDistributionClass) # correct reference again so later build targets work properly
        
    def __createBinaryDistribution(self, startScripts):
        """ 
        Creates a binary DataFinder distribution for Linux/Windows platforms
        including the Python interpreter.
        
        @param startScripts: Contains a list of start scripts for which executables are generated. The scripts
                             are described by tuples of script path and a boolean indicating whether 
                             on the Windows platform a console window is visible or not.
        @type startScripts: C{list} of C{tuple} (C{unicode}/C{string}, C{bool})
        """
       
        forcedIncludes = _forcedIncludes[:]
        if sys.platform == "win32":
            forcedIncludes.extend(_win32ForcedIncludes)
        freezer = Freezer(self.destinationPath, includes=forcedIncludes)
        freezer.include_py = not self.excludepythonshell
        for scriptPath, guiOnly in startScripts:
            freezer.addScript(scriptPath, gui_only=guiOnly)
        
        # create distribution
        freezer()
        
        # copy readme and license file
        shutil.copy(self.__buildConfiguration.readmeFile, self.destinationPath)
        shutil.copy(self.__buildConfiguration.licenseFile, self.destinationPath)
        shutil.copy(self.__buildConfiguration.changesFile, self.destinationPath)
        
        # copy image files
        if self.__buildConfiguration.includeClients:
            destinationImagePath = os.path.join(self.destinationPath, self.__buildConfiguration.imageDirectory)
            os.makedirs(destinationImagePath)
            baseImageDir = self.__buildConfiguration.imageDirectory
            for imageName in os.listdir(baseImageDir):
                if imageName.endswith(".ico") or imageName.endswith(".png"):
                    shutil.copy(os.path.join(baseImageDir, imageName), 
                                destinationImagePath)
