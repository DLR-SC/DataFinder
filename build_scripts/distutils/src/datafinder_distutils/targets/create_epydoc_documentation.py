# pylint: disable-msg=C0103
#
# Created: 30.07.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: create_epydoc_documentation.py 3603 2008-12-01 13:26:31Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Target for creating epydoc documentation. 
"""


import os
from distutils.cmd import Command


__version__ = "$LastChangedRevision: 3603 $"


class create_epydoc_documentation(Command):
    """ Creates Epydoc documentation. """
    
    description = "Creates Epydoc documentation."
    user_options = [("epydoccommand=", 
                     None, 
                     "Path and name of the epydoc command line tool")]
    __epydocCommandTemplate = "%s --config build_scripts/configuration/epydoc.cfg" 
    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.verbose = None
        self.epydoccommand = None
        Command.__init__(self, distribution)

    def initialize_options(self):
        """ Definition of command options. """
        
        self.verbose = False
        self.epydoccommand = "epydoc"

    def finalize_options(self):
        """ Set final values of options. """
        
        self.verbose = self.distribution.verbose
        
    def run(self):
        """ Perform command actions. """
        
        epydocCommand = self.__epydocCommandTemplate % self.epydoccommand
        if self.verbose:
            print(epydocCommand)
        os.system(epydocCommand)
