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


class _pylint(Command):
    """ Runs the pylint command. """

    description = "Runs the pylint command."
    user_options = [("pylintcommand=",
                     None,
                     "Path and name of the pylint command line tool"),
                     ("outputformat=",
                     None,
                     "Specifies the output type (html or parsable)")]
    __configurationPath = os.path.realpath("build_scripts/configuration/pylintrc")
    __pylintCommandTemplate = "%s --rcfile=\"%s\" --output-format=%s " \
                            + "datafinder%s"

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

        # Hudson needs parseable output in one file to work correctly
        if self.outputformat == 'parseable':
            redirection = " > pylint.txt"
        else:
            redirection = " > pylint.html"
        currentDirectory = os.path.realpath(os.curdir)
        pylintCommand = self.__pylintCommandTemplate % (self.pylintcommand,
                                                        self.__configurationPath,
                                                        self.outputformat,
                                                        redirection)
        os.chdir(os.path.realpath(self.__buildConfiguration.pylintResultDirectory))
        try:
            if self.verbose:
                print(pylintCommand)
            os.system(pylintCommand)
        finally:
            os.chdir(currentDirectory)
