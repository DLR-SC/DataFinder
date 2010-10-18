# pylint: disable-msg=C0103
#
# Created: 15.10.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id$ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Runs pylint for coding standards compliance check and determines the code coverage.
"""


from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$LastChangedRevision$"


class audit(Command):
    """ Runs pylint for coding standards compliance check and determines the code coverage. """

    description = "Runs pylint for coding standards compliance check and determines the code coverage."
    user_options = [("outputformat=",
                     None,
                     "Specifies the output type (html or parsable)")]
    sub_commands = [("gen", None), ("_pylint", None), ("test", None)]

    def __init__(self, distribution):
        """ Constructor. """

        Command.__init__(self, distribution)
        self.__buildConfiguration = BuildConfiguration()
        
    def initialize_options(self):
        """ Definition of command options. """

        self.outputformat = "html"
    
    def finalize_options(self):
        """ Set final values of options. """

        pass

    def run(self):
        """ Perform command actions. """

        # Adjust test command parameters
        testOptions = self.distribution.get_option_dict("test")
        testOptions["outputformat"] = ("", "coverage")
        if self.outputformat == "html":
            testOptions["outputformat"] = ("", "html")
        else:
            testOptions["outputformat"] = ("", "coverage")
        
        pylintOptions = self.distribution.get_option_dict("_pylint")
        if self.outputformat == "html":
            pylintOptions["outputformat"] = ("", "html")
        else:
            pylintOptions["outputformat"] = ("", "parseable")
            
        # Run commands
        for commandName in self.get_sub_commands():
            self.run_command(commandName)
