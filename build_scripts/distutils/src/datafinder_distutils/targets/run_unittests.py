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


__version__ = "$LastChangedRevision: 4538 $"


class run_unittests(Command):
    """ Runs all unit tests. """

    description = "Runs all unit tests."
    user_options = [("nosecommand=",
                     None,
                     "Path and name of the nose command."),
                     ("outputformat=",
                      None,
                      "Specifies the output format of the test results." \
                      + "Formats: xml, coverage, standard out. Default: standard out.")]

    def __init__(self, distribution):
        """ Constructor. """

        self.verbose = None
        self.nosecommand = None
        self.outputformat = None
        Command.__init__(self, distribution)

    def initialize_options(self):
        """ Definition of command options. """

        self.nosecommand = "nosetests"
        self.outputformat = None
        self.verbose = False

    def finalize_options(self):
        """ Set final values of options. """

        self.verbose = self.distribution.verbose

    def run(self):
        """ Perform command actions. """

        testdir = os.path.join("test", "unittest")
        if not self.outputformat is None and self.outputformat == "xml":
            noseTemplate = "--with-xunit --xunit-file=build/unittest/xunit.xml %s"
        elif not self.outputformat is None and self.outputformat == "coverage":
            noseTemplate = "--with-coverage --cover-erase --cover-inclusive %s src"
        else:
            noseTemplate = "--verbosity=2 -d %s"
        noseCommand = self.nosecommand + " " + noseTemplate % (testdir)

        if self.verbose:
            print(noseCommand)
            print(os.path.realpath(os.curdir))
        os.system(noseCommand)
