# pylint: disable-msg=C0103
#
# Created: 04.08.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: create_nsis_installer.py 4618 2010-04-18 12:07:08Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
This module implements a build target for creation Windows installer based on NSIS.
"""


import os
import sys

from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$LastChangedRevision: 4618 $"


_nsisDefinitions = """
!define PRODUCT_NAME "%s"
!define PRODUCT_VERSION "%s"
!define PRODUCT_PUBLISHER "%s"
!define PRODUCT_WEB_SITE "%s"
!define INSTALLER_OUTFILE "%s"
!define DISTRIBUTION_DIR "%s"
!define START_URL "%s"
!define USER_CLIENT_ICON "%s"
!define ADMIN_CLIENT_ICON "%s"
!define USER_CLIENT_EXECUTABLE_NAME "%s"
!define ADMIN_CLIENT_EXECUTABLE_NAME "%s"
"""

_nsisWithUserClientDef = "!define WITH_USER_CLIENT"
_nsisWithAdminClientDef = "!define WITH_ADMIN_CLIENT"

_nsisCommandTemplate = "%s \"%s\""


class _bdist_nsis(Command):
    """ Implements build target for creation of Windows installer based on NSIS. """
    
    description = "Creates the NSIS installer." 
    user_options = [("nsiscommand=", 
                     None, 
                     "Name and path to the NSIS compile command."),
                    ("nsismainscript=",
                     None,
                     "Name and path of the NSIS main script."),
                    ("nsisdefinitions=",
                     None,
                     "Name and path of the NSIS definition file that is generated."),
                    ("usericonname=",
                     None,
                     "Name of the user client icon. Expected in the general image resource folder."),
                    ("adminiconname=",
                     None,
                     "Name of the administration client icon. Expected in the general image resource folder."),
                    ("starturl=",
                     None,
                     "Start URL that is set during installation process.")]
    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.verbose = None
        self.nsiscommand = None
        self.nsismainscript = None
        self.nsisdefinitions = None
        self.starturl = None
        self.usericonname = None
        self.adminiconname = None
        
        Command.__init__(self, distribution)
        self.__buildConfiguration = BuildConfiguration()
        self.__userClientExecutable = os.path.basename(self.__buildConfiguration.userClientStartScript)
        self.__userClientExecutable = self.__userClientExecutable.replace(".py", ".exe")
        self.__adminClientExecutable = os.path.basename(self.__buildConfiguration.adminClientStartScript)
        self.__adminClientExecutable = self.__adminClientExecutable.replace(".py", ".exe")
        self.__sourceDistributionDirectory = os.path.join(self.__buildConfiguration.buildDirectory,
                                                          self.__buildConfiguration.fullName + "_" + sys.platform)

    def initialize_options(self):
        """ Definition of command options. """
        
        self.verbose = False
        
    def finalize_options(self):
        """ Set final values of options. """
        
        self.verbose = self.distribution.verbose
        
    def run(self):
        """ Perform command actions. """

        # Run sub commands
        for commandName in self.get_sub_commands():
            self.run_command(commandName)
        
        # Create NSIS installer       
        baseName = self.__buildConfiguration.fullName + "%s.exe"
        releaseVersions = os.environ.get("GENERATE_RELEASE_VERSIONS")
        if releaseVersions is None:
            self._createNsisInstaller(baseName % "_User+Admin", True, True)
            self._createNsisInstaller(baseName % "_User", True, False)
            self._createNsisInstaller(baseName % "_Admin", False, True)
        else:
            nameStartUrls = releaseVersions.split(";")
            for nameAndStarturl in nameStartUrls:
                if len(nameAndStarturl) > 0:
                    nameSuffix, self.starturl = nameAndStarturl.split(":", 1)
                    self._createNsisInstaller(baseName % ("-" + nameSuffix + "_User+Admin"), True, True)
                    self._createNsisInstaller(baseName % ("-" + nameSuffix + "_User"), True, False)
                    self._createNsisInstaller(baseName % ("-" + nameSuffix + "_Admin"), False, True)

    def _createNsisInstaller(self, name, withUserClient, withAdminClient):
        """ Creates the different variables for the NSIS installer script. """
        
        installerPath = os.path.join(os.path.realpath(self.__buildConfiguration.distDirectory), name)

        normedImageDir = os.path.normpath(self.__buildConfiguration.imageDirectory)
        userIconPath = os.path.join(normedImageDir, self.usericonname)
        adminIconPath = os.path.join(normedImageDir, self.adminiconname)
        nsisDefs = _nsisDefinitions % (self.__buildConfiguration.name,
                                       self.__buildConfiguration.version,
                                       self.__buildConfiguration.author,
                                       self.__buildConfiguration.url,
                                       installerPath,
                                       os.path.realpath(self.__sourceDistributionDirectory),
                                       self.starturl,
                                       userIconPath,
                                       adminIconPath,
                                       self.__userClientExecutable,
                                       self.__adminClientExecutable)
        if withUserClient:
            nsisDefs += _nsisWithUserClientDef
        if withAdminClient:
            nsisDefs += "\n" + _nsisWithAdminClientDef
        fileHandle = open(self.nsisdefinitions, "wb")
        fileHandle.write(nsisDefs)
        fileHandle.close()
        
        # Create installer
        if self.verbose:
            print("Running " + _nsisCommandTemplate % (self.nsiscommand,
                                                       os.path.realpath(self.nsismainscript)))
        os.system(_nsisCommandTemplate % (self.nsiscommand,
                                          os.path.realpath(self.nsismainscript)))
