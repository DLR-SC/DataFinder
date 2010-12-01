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
Tests the data format registry.
"""


import unittest

from datafinder.core.configuration.dataformats.dataformat import DataFormat
from datafinder.core.configuration.dataformats.registry import DataFormatRegistry


__version__ = "$Revision-Id:$" 


class RegistryTest(unittest.TestCase):
    """ Tests the data format registry. """
    
    def setUp(self):
        """ Creates test setup. """

        self._registry = DataFormatRegistry()

    def testLoad(self):
        """ Test the load interface. """
        
        testDataFormat = DataFormat("PDF")
        self.assertFalse(self._registry.hasDataFormat(testDataFormat))
        self._registry.load()
        self.assertTrue(self._registry.hasDataFormat(testDataFormat))
        
    def testRegisterUnregister(self):
        """ Tests how registration and unregistration works. """
        
        dataFormat = DataFormat("TestFormat", ["testmime"], "icon", [".test"])
        self._registry.register(dataFormat)
        self.assertTrue(self._registry.hasDataFormat(dataFormat))
        self.assertEquals(self._registry.determineDataFormat(mimeType="testmime"), dataFormat)
        self.assertEquals(self._registry.determineDataFormat(baseName="test.test"), dataFormat)
        
        dataFormat.iconName = "NewIcon"
        self._registry.register(dataFormat)
        self.assertTrue(self._registry.hasDataFormat(dataFormat))
        self.assertEquals(self._registry.getDataFormat("TestFormat").iconName, "NewIcon")
        
        self._registry.unregister(dataFormat)
        self.assertFalse(self._registry.hasDataFormat(dataFormat))
        self.assertEquals(self._registry.getDataFormat("TestFormat"), self._registry.defaultDataFormat)
        self.assertEquals(self._registry.determineDataFormat(mimeType="testmime"), self._registry.defaultDataFormat)
        self.assertEquals(self._registry.determineDataFormat(baseName="test.test"), self._registry.defaultDataFormat)
        
    def testDetermineDataFormat(self):
        """ Test how the determination of the data type works. """
        
        self._registry.load()
        
        self.assertEquals(self._registry.determineDataFormat(mimeType="application/msword").name, "WORD")
        self.assertEquals(self._registry.determineDataFormat(baseName="t.doc").name, "WORD")
        
        self.assertEquals(self._registry.determineDataFormat(mimeType="application/vnd.ms-excel").name, "EXCEL")
        self.assertEquals(self._registry.determineDataFormat(baseName="t.xls").name, "EXCEL")
        
        self.assertEquals(self._registry.determineDataFormat(mimeType="application/vnd.ms-powerpoint").name, "POWERPOINT")
        self.assertEquals(self._registry.determineDataFormat(baseName="t.ppt").name, "POWERPOINT")
        
        self.assertEquals(self._registry.determineDataFormat(mimeType="application/pdf").name, "PDF")
        self.assertEquals(self._registry.determineDataFormat(baseName="t.pdf").name, "PDF")
        
        self.assertEquals(self._registry.determineDataFormat(mimeType="text/xml").name, "XML")
        self.assertEquals(self._registry.determineDataFormat(baseName="t.xml").name, "XML")

        self.assertEquals(self._registry.determineDataFormat(mimeType="text/html").name, "HTML")
        self.assertEquals(self._registry.determineDataFormat(baseName="test.htm").name, "HTML")
        
        self.assertEquals(self._registry.determineDataFormat(mimeType="text/x-python").name, "PYTHON")
        self.assertEquals(self._registry.determineDataFormat(baseName="t.pyc").name, "PYTHON")
        
        self.assertEquals(self._registry.determineDataFormat(mimeType="application/octet-stream").name, "BINARY")
        self.assertEquals(self._registry.determineDataFormat(baseName="t.bin").name, "BINARY")
        
        self.assertEquals(self._registry.determineDataFormat(mimeType="text/plain").name, "TEXT")
        self.assertEquals(self._registry.determineDataFormat(baseName="test.log").name, "TEXT")
       
        self.assertEquals(self._registry.determineDataFormat(mimeType="application/x-tar").name, "ARCHIVE")
        self.assertEquals(self._registry.determineDataFormat(baseName="test.rar").name, "ARCHIVE")
        
        self.assertEquals(self._registry.determineDataFormat(mimeType="audio/x-wav").name, "AUDIO")
        self.assertEquals(self._registry.determineDataFormat(baseName="test.ogg").name, "AUDIO")
        
        self.assertEquals(self._registry.determineDataFormat(mimeType="video/mpeg").name, "VIDEO")
        self.assertEquals(self._registry.determineDataFormat(baseName="t.avi").name, "VIDEO")
        
        self.assertEquals(self._registry.determineDataFormat(mimeType="image/jpeg").name, "IMAGE")
        self.assertEquals(self._registry.determineDataFormat(baseName="test.bmp").name, "IMAGE")
        
        self.assertEquals(self._registry.determineDataFormat(baseName="test.vsd").name, "VISIO")
