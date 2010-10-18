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
Performs common preparation tasks, e.g. build directory creation.
"""


import os
from distutils.cmd import Command

from datafinder_distutils.configuration import BuildConfiguration


__version__ = "$LastChangedRevision$"


class _prepare(Command):
    """ Implements common preparation tasks. """

    description = "Private build command performing common preparation tasks."
    user_options = list()


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

        if not os.path.isdir(self.__buildConfiguration.buildDirectory):
            os.mkdir(self.__buildConfiguration.buildDirectory)
        if not os.path.isdir(self.__buildConfiguration.epydocResultDirectory):
            os.mkdir(self.__buildConfiguration.epydocResultDirectory)
        if not os.path.isdir(self.__buildConfiguration.pylintResultDirectory):
            os.mkdir(self.__buildConfiguration.pylintResultDirectory)
        if not os.path.isdir(self.__buildConfiguration.distDirectory):
            os.mkdir(self.__buildConfiguration.distDirectory)
        if not os.path.isdir(self.__buildConfiguration.unittestResultDirectory):
            os.mkdir(self.__buildConfiguration.unittestResultDirectory)
