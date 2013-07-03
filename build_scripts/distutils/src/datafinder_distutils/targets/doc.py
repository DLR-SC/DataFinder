# pylint: disable=C0103
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#met:
#
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer. 
#
# * Redistributions in binary form must reproduce the above copyright 
#   notice, this list of conditions and the following disclaimer in the 
#   documentation and/or other materials provided with the 
#   distribution. 
#
# * Neither the name of the German Aerospace Center nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
#OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  


""" 
Target for creating epydoc documentation. 
"""


import os
from distutils.cmd import Command


__version__ = "$Revision-Id:$" 


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
    __epydocCommandTemplate = "%s --parse-only --no-sourcecode --html %s %s"

    
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
