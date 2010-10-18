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


class doc(Command):
    """ Creates Epydoc documentation. """
    
    description = "Creates Epydoc documentation."
    user_options = [("epydoccommand=", 
                     None, 
                     "Path and name of the epydoc command line tool."),
                     ("modules=", 
                     None, 
                     "Colon separated list of modules which should be documented."),
                     ("destdir=", 
                     None, 
                     "Path to directory which should contain the documentation.")]
    __epydocCommandTemplate = "%s --no-sourcecode --html %s %s"

    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.verbose = None
        self.epydoccommand = None
        self.modules = None
        self.destdir = None
        Command.__init__(self, distribution)

    def initialize_options(self):
        """ Definition of command options. """
        
        self.verbose = False
        self.epydoccommand = "epydoc"

    def finalize_options(self):
        """ Set final values of options. """
        
        if not self.modules is None:
            self.modules = self.modules.replace(";", " ")
        self.verbose = self.distribution.verbose
        
    def run(self):
        """ Perform command actions. """

        modules = self.modules or ""
        destdir = ""
        if not self.destdir is None:
            destdir = "--output=%s" % self.destdir
        epydocCommand = self.__epydocCommandTemplate % (self.epydoccommand, destdir, modules)
        if self.verbose:
            print(epydocCommand)
        os.system(epydocCommand)
