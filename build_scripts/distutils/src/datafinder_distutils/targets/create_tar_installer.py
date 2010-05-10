# pylint: disable-msg=C0103
#
# Created: 27.08.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: create_tar_installer.py 3603 2008-12-01 13:26:31Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
This module implements a build target for creation tar archives usable for installation.
"""


import sys
import os
import tarfile
from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$LastChangedRevision: 3603 $"


class create_tar_installer(Command):
    """ Implements build target for creation of tar archives usable for installation. """
    
    description = "Creates tar distribution archives." 
    user_options = list()
    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.verbose = None
        self.outputdirectory = None
        
        Command.__init__(self, distribution)
        self.__buildConfiguration = BuildConfiguration()
        
    def initialize_options(self):
        """ Definition of command options. """
        
        self.verbose = False
        
    def finalize_options(self):
        """ Set final values of options. """
        
        self.verbose = self.distribution.verbose
        
    def run(self):
        """ Perform command actions. """
       
        baseName = self.__buildConfiguration.fullName + "%s"
        
        self.__createTar(baseName % "_User+Admin", True, True)
        self.__createTar(baseName % "_User", True, False)
        self.__createTar(baseName % "_Admin", False, True)
        
    def __createTar(self, name, withUserClient, withAdminClient):
        """ Creates the different variables for the NSIS installer script. """
        
        installerPath = os.path.join(os.path.realpath(self.__buildConfiguration.distDirectory), name + ".tar.gz")
        sourceDistributionDirectory = os.path.join(self.__buildConfiguration.buildDirectory,
                                                   self.__buildConfiguration.fullName + "_" + sys.platform)
        if self.verbose:
            print("Create archive '%s'." % installerPath)
        
        ignoreFiles = list()
        if not withUserClient:
            ignoreFiles.append(os.path.basename(self.__buildConfiguration.userClientStartScript)[:-3])
        if not withAdminClient:
            ignoreFiles.append(os.path.basename(self.__buildConfiguration.adminClientStartScript)[:-3])
        tarFile = tarfile.open(installerPath, "w:gz")
        for fileName in os.listdir(sourceDistributionDirectory):
            ignoreFileName = False
            for ignoreFile in ignoreFiles:
                if ignoreFile == fileName or \
                   ignoreFile + "." in fileName:
                    ignoreFileName = True
            if not ignoreFileName:
                tarFile.add(os.path.join(sourceDistributionDirectory, fileName),
                            arcname=os.path.join(name, fileName))
        tarFile.close()
