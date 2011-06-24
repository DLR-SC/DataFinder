# pylint: disable=C0103
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#met:
#
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer. 
#
# * Redistributions in binary form must reproduce the above copyright 
#   notice, this list of conditions and the following disclaimer in the 
#   documentation and/or other materials provided with the 
#   distribution. 
#
# * Neither the name of the German Aerospace Center nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
#OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  


""" 
This module implements a build target for creation Windows installer based on NSIS.
"""


import os
import sys

from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$Revision-Id:$" 


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
        self._createNsisInstaller(baseName % "_User+Admin", True, True)
        self._createNsisInstaller(baseName % "_User", True, False)
        self._createNsisInstaller(baseName % "_Admin", False, True)
        if not releaseVersions is None:
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
