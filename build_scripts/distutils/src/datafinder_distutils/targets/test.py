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
import sys

from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$LastChangedRevision: 4538 $"


_UNITTEST_OUTPUT_DIR = "build/unittest"
_NOSE_DEFAULT_SCRIPT = "nosetests-script.py"

class test(Command):
    """ Runs all unit tests. """

    description = "Runs all unit tests."
    user_options = [("nosecommand=",
                     None,
                     "Path and name of the nose command."),
                     ("outputformat=",
                      None,
                      "Specifies the output format of the test results." \
                      + "Formats: xml, standard out. Default: standard out."),
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

        self.nosecommand = _NOSE_DEFAULT_SCRIPT
        self.outputformat = None
        self.coveragecommand = "coverage"
        self.coverageoutputformat = None
        self.verbose = False

    def finalize_options(self):
        """ Set final values of options. """

        self.verbose = self.distribution.verbose
        if sys.platform == "win32" and self.nosecommand == _NOSE_DEFAULT_SCRIPT:
            self.nosecommand = os.path.join(os.path.normpath(sys.exec_prefix), "Scripts", self.nosecommand)
            
    def run(self):
        """ Perform command actions. """

        # Run sub commands
        for commandName in self.get_sub_commands():
            self.run_command(commandName)
            
        # Run tests
        testdir = os.path.join("test", "unittest")
        if self.outputformat == "xml":
            noseOptions = "--with-xunit --xunit-file=" + _UNITTEST_OUTPUT_DIR + "/xunit.xml %s" 
        else:
            noseOptions = "--verbosity=2 -d %s"
        
        noseCommand = self.nosecommand + " " + noseOptions % (testdir)
        if not self.coverageoutputformat is None:
            noseCommand = self.coveragecommand \
                        + " run --branch --source=src/datafinder,test/unittest/datafinder_test " \
                        + noseCommand
        else:
            noseCommand = "%s %s" % (sys.executable, noseCommand) 
                        
        if self.verbose:
            print(noseCommand)
        os.system(noseCommand)

        if not self.coverageoutputformat is None:
            if self.coverageoutputformat == "html":
                coverageCommand = "%s %s --omit=*gen* -d %s" % (self.coveragecommand, 
                                                   self.coverageoutputformat, 
                                                   _UNITTEST_OUTPUT_DIR)
            else: # xml
                coverageCommand = "%s %s --omit=*gen*" % (self.coveragecommand, self.coverageoutputformat)
            
            if self.verbose:
                print(coverageCommand)
            os.system(coverageCommand)
            
    def _runGenTarget(self):
        """ Checks whether the gen build target is available. Within a source
        distribution this may not the case. """

        return os.path.exists(os.path.join(self.__buildConfiguration.distutilTargetPackagePath, 
                                           "gen.py"))
    
    
    sub_commands = [("_prepare", None), ("gen", _runGenTarget)]
