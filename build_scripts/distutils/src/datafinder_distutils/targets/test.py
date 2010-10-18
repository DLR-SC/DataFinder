# pylint: disable-msg=C0103,R0912
#
# Created: 31.07.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: run_unittests.py 4538 2010-03-08 19:33:13Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder/
#


"""
This module provides the target for running the unit tests.
"""


import os

from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$LastChangedRevision: 4538 $"


_UNITTEST_OUTPUT_DIR = "build/unittest"


class test(Command):
    """ Runs all unit tests. """

    description = "Runs all unit tests."
    user_options = [("nosecommand=",
                     None,
                     "Path and name of the nose command."),
                     ("outputformat=",
                      None,
                      "Specifies the output format of the test results." \
                      + "Formats: xml, coverage, standard out. Default: standard out."),
                      ("coveragecommand=",
                      None,
                      "Optionally, path and name of the coverage command."),
                      ("coverageoutputformat=",
                      None,
                      "Specifies the output format of the coverage report." \
                      + "Formats: xml, html. Default: html")]


    def __init__(self, distribution):
        """ Constructor. """

        self.verbose = None
        self.nosecommand = None
        self.outputformat = None
        self.coveragecommand = None
        self.coverageoutputformat = None
        self.__buildConfiguration = BuildConfiguration()
        Command.__init__(self, distribution)

    def initialize_options(self):
        """ Definition of command options. """

        self.nosecommand = "nosetests"
        self.outputformat = None
        self.coveragecommand = "coverage"
        self.coverageoutputformat = "html"
        self.verbose = False

    def finalize_options(self):
        """ Set final values of options. """

        self.verbose = self.distribution.verbose

    def run(self):
        """ Perform command actions. """

        # Run sub commands
        for commandName in self.get_sub_commands():
            self.run_command(commandName)
            
        # Run tests
        testdir = os.path.join("test", "unittest")
        if not self.outputformat is None and self.outputformat == "xml":
            noseOptions = "--with-xunit --xunit-file=" + _UNITTEST_OUTPUT_DIR + "/xunit.xml %s" 
        elif not self.outputformat is None and self.outputformat == "coverage":
            noseOptions = "--with-coverage --cover-erase --cover-inclusive %s src"
        else:
            noseOptions = "--verbosity=2 -d %s"
        noseCommand = self.nosecommand + " " + noseOptions % (testdir)

        if self.verbose:
            print(noseCommand)
        os.system(noseCommand)
        
        if self.outputformat == "coverage":
            coverageCommand = "%s %s -d %s" % (self.coveragecommand, 
                                               self.coverageoutputformat, 
                                               _UNITTEST_OUTPUT_DIR)
            if self.verbose:
                print(coverageCommand)
            os.system(coverageCommand)
            
    def _runGenTarget(self):
        """ Checks whether the gen build target is available. Within a source
        distribution this may not the case. """

        return os.path.exists(os.path.join(self.__buildConfiguration.distutilTargetPackagePath, 
                                           "gen.py"))
    
    
    sub_commands = [("_prepare", None), ("gen", _runGenTarget)]
