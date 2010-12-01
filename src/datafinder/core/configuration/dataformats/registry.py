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
Implements a registry for data formats.
"""


from copy import copy
from mimetypes import guess_type

from datafinder.core.configuration.dataformats.dataformat import DataFormat


__version__ = "$Revision-Id:$" 


class DataFormatRegistry(object):
    """ Implements a registry for data formats. """
    
    __DEFAULT_DATAFORMAT = DataFormat("Default")
    
    def __init__(self):
        """ Constructor. """
        
        self._nameDataFormatMap = dict()
        self._mimeTypeDataFormatMap = dict()
        self._fileSuffixDataFormatMap = dict()
    
    def load(self):
        """ Initializes the data format registry. """
        
        self.__registerStandardDataFormats()
            
    def __registerStandardDataFormats(self):
        """ Registers the standard data formats. """
        
        self.register(DataFormat("WORD", ["application/msword"], "doc_format"))
        self.register(DataFormat("EXCEL", ["application/vnd.ms-excel"], "xls_format"))
        self.register(DataFormat("POWERPOINT", ["application/vnd.ms-powerpoint"], "ppt_format"))
        self.register(DataFormat("PDF", ["application/pdf"], "pdf_format"))
        self.register(DataFormat("XML", ["text/xml", "application/xml"], "xml_format", [".xml"]))
        self.register(DataFormat("HTML", ["text/html"], "html_format"))
        self.register(DataFormat("PYTHON", ["text/x-python"], "py_format", [".pyc", ".pyd"]))
        self.register(DataFormat("BINARY", ["application/octet-stream"], "bin_format", [".bin"]))
        self.register(DataFormat("TEXT", ["text/plain"], "txt_format", [".log", ".java", ".cpp", ".js", ".php", ".csv", ".ini", ".rtf"]))
        self.register(DataFormat("ARCHIVE", ["application/zip", "application/x-tar"], "zip_format", [".7z", ".bz2", ".rar"]))
        self.register(DataFormat("AUDIO", ["audio/mpeg", "audio/x-wav", "audio/midi"], "audio_format", [".ogg", ".wma"]))
        self.register(DataFormat("VIDEO", ["video/mpeg", "video/x-msvideo", "video/quicktime"], "video_format", [".xvid"]))
        self.register(DataFormat("IMAGE", ["image/jpeg", "image/tiff"], "image_format", [".gif", ".png", ".eps", ".bmp"]))
        self.register(DataFormat("VISIO", [], "vsd_format", [".vsd"]))
        
    def register(self, dataFormat):
        """ 
        Registers a data format. If a data format with the given name
        already exists, it will be replaced.
        
        @param dataFormat: The format which has to be registered. 
        @type dataFormat: L{DataFormat<datafinder.core.configuration.dataformats.dataformat.DataFormat>}
        """
        
        self.unregister(dataFormat)
    
        self._nameDataFormatMap[dataFormat.name] = dataFormat
        for mimeType in dataFormat.mimeTypes:
            if mimeType in self._mimeTypeDataFormatMap:
                self._mimeTypeDataFormatMap[mimeType].append(dataFormat)
            else:
                self._mimeTypeDataFormatMap[mimeType] = [dataFormat]
        
        for fileSuffix in dataFormat.additionalFileSuffixes:
            if fileSuffix in self._fileSuffixDataFormatMap:
                self._fileSuffixDataFormatMap[fileSuffix].append(dataFormat)
            else:
                self._fileSuffixDataFormatMap[fileSuffix] = [dataFormat]
        
    def unregister(self, dataFormat):
        """ 
        Unregisters the given data format.
        
        @param dataFormat: The format which has to be unregistered. 
        @type dataFormat: L{DataFormat<datafinder.core.configuration.dataformats.dataformat.DataFormat>}
        """
        
        if dataFormat.name in self._nameDataFormatMap:
            del self._nameDataFormatMap[dataFormat.name]
            
            for mimeType in dataFormat.mimeTypes:
                if mimeType in self._mimeTypeDataFormatMap:
                    self._mimeTypeDataFormatMap[mimeType].remove(dataFormat)
                    if len(self._mimeTypeDataFormatMap[mimeType]) == 0:
                        del self._mimeTypeDataFormatMap[mimeType]
                        
            for fileSuffix in dataFormat.additionalFileSuffixes:
                if fileSuffix in self._fileSuffixDataFormatMap:
                    self._fileSuffixDataFormatMap[fileSuffix].remove(dataFormat)
                    if len(self._fileSuffixDataFormatMap[fileSuffix]) == 0:
                        del self._fileSuffixDataFormatMap[fileSuffix]

    def hasDataFormat(self, dataFormat):
        """ 
        Checks whether the specific data format exists. 
        
        @param dataFormat: The format which has to be unregistered. 
        @type dataFormat: L{DataFormat<datafinder.core.configuration.dataformats.dataformat.DataFormat>}
        
        @return: Flag indicating whether it is registered.
        @rtype: C{bool}
        """
        
        return dataFormat.name in self._nameDataFormatMap
    
    def getDataFormat(self, name):
        """
        Retrieves the data format for the given name or C{None}.
        
        @param name: Name of the data format.
        @type name: C{unicode}
        
        @return: The data format associated with C{name}.
        @rtype: L{DataFormat<datafinder.core.configuration.dataformats.dataformat.DataFormat>}
        """
        
        if name in self._nameDataFormatMap:
            dataFormat = self._nameDataFormatMap[name]
        else:
            dataFormat = self.defaultDataFormat
        return dataFormat
    
    def determineDataFormat(self, dataFormatName=None, mimeType=None, baseName=None):
        """
        Determines the data format using the given data format name, MIME type, base name.
        
        @param dataFormatName: Explicit name of a data format or C{None} which is the default value.
        @type dataFormatName: C{unicode}
        @param mimeType: MIME type or C{None} which is the default value.
        @type mimeType: C{unicode}
        @param mimeType: Base name or C{None} which is the default value.
        @type mimeType: C{unicode}
        """
        
        if not dataFormatName is None:
            dataFormat = self.getDataFormat(dataFormatName)
        else:
            dataFormat = self._determineDataFormat(mimeType, baseName)
        return dataFormat
    
    def _determineDataFormat(self, mimeType=None, baseName=None):
        """
        Guesses the data format for the given MIME type and/or base name.
        First a MIME type based resolution is tried. Otherwise the file suffix
        of the base name is explicitly used to resolve the data format. If everything
        fails, the default data format is returned.
        """
        
        dataFormat = None
        if mimeType is None and baseName is None:
            dataFormat = self.defaultDataFormat
        else:
            if mimeType is None:
                mimeType = guess_type(baseName, False)[0]
            if mimeType is None:
                dataFormat = self._determineDataFormatUsingFileSuffix(baseName)
            else:
                mimeType = mimeType.lower()
                if mimeType in self._mimeTypeDataFormatMap:
                    dataFormat = self._mimeTypeDataFormatMap[mimeType][0]
                elif not baseName is None:
                    dataFormat = self._determineDataFormatUsingFileSuffix(baseName)
                else:
                    dataFormat = self.defaultDataFormat
        return dataFormat
    
    def _determineDataFormatUsingFileSuffix(self, baseName):
        """ Determines the file data format using the file suffix. """
        
        startPosition = baseName.rfind(".")
        if startPosition != -1:
            fileSuffix = baseName[startPosition:]
            fileSuffix = fileSuffix.lower()
            if fileSuffix in self._fileSuffixDataFormatMap:
                dataFormat = self._fileSuffixDataFormatMap[fileSuffix][0]
            else:
                dataFormat = self.defaultDataFormat
        else:
            dataFormat = self.defaultDataFormat
        return dataFormat
    
    @property    
    def defaultDataFormat(self):
        """ Returns the default data format. """
        
        return copy(self.__DEFAULT_DATAFORMAT)
