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
Implements the general command for generating Python code.
"""


from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$LastChangedRevision$"


class gen(Command):
    """ Implements the general command for generating Python code. """

    description = "Generates Python modules from XML schema and Qt designer files."
    user_options = list()
    sub_commands = [("_prepare", None),
                    ("_gen_configuration_modules", None), 
                    ("_gen_qt3gui_modules", None), 
                    ("_gen_qt4gui_modules", None)]


    def __init__(self, distribution):
        """ Constructor. """

        Command.__init__(self, distribution)
        self.__buildConfiguration = BuildConfiguration()
        
    def initialize_options(self):
        """ Definition of command options. """

        pass
    
    def finalize_options(self):
        """ Set final values of options. """

        pass

    def run(self):
        """ Perform command actions. """

        # Run sub commands
        for commandName in self.get_sub_commands():
            self.run_command(commandName)
