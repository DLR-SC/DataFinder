# pylint: disable=C0103
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
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
This module provides the target for running pylint on the sources
in the DataFinder package.
"""


import os
from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$Revision-Id:$" 


_PARSEABLE_OUTPUT_OPTION = "parseable"
_PYLINT_OUPUT_FILENAME = "pylint.txt"


class _pylint(Command):
    """ Runs the pylint command. """

    description = "Runs the pylint command."
    user_options = [("pylintcommand=",
                     None,
                     "Path and name of the pylint command line tool"),
                     ("outputformat=",
                     None,
                     "Specifies the output type (html or parseable)")]
    __configurationPath = os.path.realpath("build_scripts/configuration/pylintrc")
    __pylintCommandTemplate = "%s --rcfile=\"%s\" --output-format=%s %s %s"
    

    def __init__(self, distribution):
        """ Constructor. """

        self.verbose = None
        self.pylintcommand = None
        self.outputformat = None
        Command.__init__(self, distribution)
        self.__buildConfiguration = BuildConfiguration()

    def initialize_options(self):
        """ Definition of command options. """

        self.verbose = False
        self.pylintcommand = "pylint"
        self.outputformat = "html"

    def finalize_options(self):
        """ Set final values of options. """

        self.verbose = self.distribution.verbose

    def run(self):
        """ Perform command actions. """

        # We have to run it twice because of problems with PyQt4 and PyQt3 imports
        # which are breaking pylint
        for index, packageName in enumerate(["datafinder", "datafinder.gui.admin"]):
            if self.outputformat == _PARSEABLE_OUTPUT_OPTION: # Basically used for CI with Hudson
                pylintOuputFilePath = "%s/%s " % (self.__buildConfiguration.pylintResultDirectory, _PYLINT_OUPUT_FILENAME)
                if index == 0:
                    redirection = " > %s" % pylintOuputFilePath 
                else:
                    redirection = " >> %s" % pylintOuputFilePath # append the rest
            else:
                redirection = " > %s/%s.html" % (self.__buildConfiguration.pylintResultDirectory, packageName)
            pylintCommand = self.__pylintCommandTemplate % (self.pylintcommand,
                                                            self.__configurationPath,
                                                            self.outputformat,
                                                            packageName,
                                                            redirection)
            if self.verbose:
                print(pylintCommand)
            os.system(pylintCommand)
            
        # Ensures that file path elements are separated by "/"
        # to avoid problems with Hudson on different platforms
        if self.outputformat == _PARSEABLE_OUTPUT_OPTION:
            fileObject = open(pylintOuputFilePath, "rb")
            content = fileObject.read().replace("\\", "/")
            fileObject.close()
            fileObject = open(pylintOuputFilePath, "wb")
            fileObject.write(content)
            fileObject.close()
