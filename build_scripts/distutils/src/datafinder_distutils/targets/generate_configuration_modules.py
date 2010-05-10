# pylint: disable-msg=C0103
#
# Created: 30.07.2008 wend_he <Heinrich.Wendel@dlr.de>
# Changed: $Id: generate_gui_modules.py 3603 2008-12-01 13:26:31Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Build Target for creation of Python modules from schemas for the configuration.
"""


import os

from distutils.cmd import Command

from datafinder_distutils import configuration


__version__ = "$LastChangedRevision: 3603 $"


class generate_configuration_modules(Command):
    """ 
    Implements build target to generate Python modules from Qt designer files.
    """
    
    description = "Generates Python modules from Qt designer files."
    
    user_options = [("generatedscommand=", 
                     None, 
                     "Path to the generateDS command."),
                     ("xsddirectory=", 
                     None,
                     "Directory of the schema files."),
                     ("genconfigurationdirectory=", 
                     None, 
                     "Directory where the python files should be created.")]

    __generatedDsCommandTemplate = "%s -m --use-old-getter-setter --no-process-includes -o %s %s"
    
    
    def __init__(self, distribution):
        """ Constructor. """
        
        self.__buildConfiguration = configuration.BuildConfiguration()
        self.generatedscommand = None
        self.genconfigurationdirectory = None
        self.xsddirectory = None
        self.verbose = None
        Command.__init__(self, distribution)
        
    def initialize_options(self):
        """ Definition of command options. """
        pass

    def finalize_options(self):
        """ Set final values of options. """
        self.verbose = self.distribution.verbose
    
    def run(self):
        """ Perform command actions. """
        self.makePackage(self.genconfigurationdirectory)
        directoryList = os.listdir(self.xsddirectory)
        for filename in directoryList:
            if not ".xsd" in filename:
                continue
            modulename = filename.replace(".xsd", ".py")
            command = self.__generatedDsCommandTemplate % (self.generatedscommand, 
                                                           os.path.join(self.genconfigurationdirectory, modulename),
                                                           os.path.join(self.xsddirectory, filename))

            if os.system(command) != 0:
                print "Failed to generate configuration class from xsd schema for file:" + filename

    @staticmethod
    def makePackage(packagePathName):
        """
        Create a new package at the given package path.

        @param packagePathName: Path of the new package.
        @type packagePathName: C{string}
        """

        if not os.path.exists(packagePathName):
            os.mkdir(packagePathName)
        for file_ in os.listdir(packagePathName):
            if ".py" in file_:
                os.remove(os.path.join(packagePathName, file_))
        initFileName = os.path.join(packagePathName, "__init__.py")
        open(initFileName, 'w').close()
