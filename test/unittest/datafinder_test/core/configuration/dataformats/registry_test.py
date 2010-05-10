#
# Created: 03.02.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: registry_test.py 4551 2010-03-15 15:43:57Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests the data format registry.
"""


import unittest

from datafinder.core.configuration.dataformats.dataformat import DataFormat
from datafinder.core.configuration.dataformats.registry import DataFormatRegistry


__version__ = "$LastChangedRevision: 4551 $"


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
