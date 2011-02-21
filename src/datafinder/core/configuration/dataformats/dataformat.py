# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
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
Implements the data format representation.
"""


from datafinder.core.configuration.dataformats.constants import DEFAULT_DATAFORMAT_ICONNAME, STANDARD_FORMAT_TYPE


__version__ = "$Revision-Id:$" 


class DataFormat(object):
    """ Represents a data type. """
    
    def __init__(self, name, mimeTypes=None, iconName=DEFAULT_DATAFORMAT_ICONNAME, additionalFileSuffixes=None, type_=STANDARD_FORMAT_TYPE):
        """ 
        Constructor. 
        
        @param name: Name of data type.
        @type name: C{unicode}
        @param mimeTypes: List of MIME types which are associated with this format.
        @type mimeTypes: C{list} of C{unicode}
        @param iconName: Symbolic name of an associated icon.
        @type iconName: C{unicode}
        @param additionalFileSuffixes: List of file suffixes which are used when a MIME type based resolution fails.
        @type additionalFileSuffixes: C{list} of C{unicode}
        @param type_: The format type. See L{constants<datafinder.core.configuration.dataformats.constants>} for details.
        @param type_: C{unicode}
        """
        
        self.name = name
        self.type = type_
        self.iconName = iconName
        self.mimeTypes = mimeTypes or list()
        self.additionalFileSuffixes = additionalFileSuffixes or list()
        
        self.description = ""
        self.propertyDefinitions = dict()
        self.printScriptName = None
        self.editScriptName = None
        self.viewScriptName = None

    def __repr__(self):
        """ Provides a readable string representation. """
        
        return self.name + " " + self.type
    
    def __cmp__(self, other):
        """ Makes the data types comparable. """
        
        try:
            return cmp(self.name, other.name)
        except AttributeError:
            return 1
