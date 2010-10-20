# pylint: disable-msg=C0103
# Created: 24.07.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: run_pylint.py 3712 2009-01-22 09:48:17Z mohr_se $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder/
#


"""
This module provides the target for running pylint on the sources
in the DataFinder package.
"""


import os
from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$LastChangedRevision: 3712 $"


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
