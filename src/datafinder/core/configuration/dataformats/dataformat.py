#
# Created: 02.02.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: dataformat.py 4430 2010-02-03 15:38:57Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the data format representation.
"""


from datafinder.core.configuration.dataformats.constants import DEFAULT_DATAFORMAT_ICONNAME, STANDARD_FORMAT_TYPE


__version__ = "$LastChangedRevision: 4430 $"


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

    def __str__(self):
        """ Provides a readable string representation. """
        
        return self.name + " " + self.type
    
    def __cmp__(self, other):
        """ Makes the data types comparable. """
        
        try:
            return cmp(self.name, other.name)
        except AttributeError:
            return 1
