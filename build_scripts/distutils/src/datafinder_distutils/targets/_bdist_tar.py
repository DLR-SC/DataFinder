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
This module implements a build target for creation tar archives usable for installation.
"""


import os
import sys
import tarfile

from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$Revision-Id:$" 


class _bdist_tar(Command):
    """ Implements build target for creation of tar archives usable for installation. """
    
    description = "Creates tar distribution archives." 
    user_options = list()
    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.verbose = None
        self.outputdirectory = None
        
        Command.__init__(self, distribution)
        self.__buildConfiguration = BuildConfiguration()
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
        
        # Create Tar archives       
        baseName = self.__buildConfiguration.fullName + "%s"
        self.__createTar(baseName % "_User+Admin", True, True)
        self.__createTar(baseName % "_User", True, False)
        self.__createTar(baseName % "_Admin", False, True)
        
    def __createTar(self, name, withUserClient, withAdminClient):
        """ Creates the different variables for the NSIS installer script. """
        
        installerPath = os.path.join(os.path.realpath(self.__buildConfiguration.distDirectory), name + ".tar.gz")
        
        if self.verbose:
            print("Create archive '%s'." % installerPath)
        
        ignoreFiles = list()
        if not withUserClient:
            ignoreFiles.append(os.path.basename(self.__buildConfiguration.userClientStartScript)[:-3])
        if not withAdminClient:
            ignoreFiles.append(os.path.basename(self.__buildConfiguration.adminClientStartScript)[:-3])
        tarFile = tarfile.open(installerPath, "w:gz")
        for fileName in os.listdir(self.__sourceDistributionDirectory):
            ignoreFileName = False
            for ignoreFile in ignoreFiles:
                if ignoreFile == fileName or \
                   ignoreFile + "." in fileName:
                    ignoreFileName = True
            if not ignoreFileName:
                tarFile.add(os.path.join(self.__sourceDistributionDirectory, fileName),
                            arcname=os.path.join(name, fileName))
        tarFile.close()
