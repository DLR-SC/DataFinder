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
Implements test cases for the WebDAV-specific file system factory.
"""


import unittest

from datafinder.persistence.adapters.sftp import factory
from datafinder.persistence.error import PersistenceError


class ParseDiskFreeOutpoutParserTestCase(unittest.TestCase):
    
    def testExpectedDefaultCase(self):
        dfOut = (
            "Filesystem     1K-blocks   Used Available Use% Mounted on\n"
            "/dev/sdb1      103079200 245600  97590824   1% /home\n")
        availableSpace = factory._parseDiskFreeCommandOutForAvailableSpace(dfOut)
        self.assertEquals(availableSpace, 99933003776)
        
    def testMultipleDevices(self):
        dfOut = (
            "Filesystem     1K-blocks   Used Available Use% Mounted on\n"
            "/dev/sdb1      103079200 245600  200   1% /home\n"
            "/dev/sdc1      103079200 245600  1000   1% /home\n")
        availableSpace = factory._parseDiskFreeCommandOutForAvailableSpace(dfOut)
        self.assertEquals(availableSpace, 204800)
        
    def testInvalidFormat(self):
        dfOut = "INVALID"
        self.assertRaises(PersistenceError, factory._parseDiskFreeCommandOutForAvailableSpace, dfOut)
    
    def testInsufficientColumns(self):
        dfOut = (
            "Filesystem     1K-blocks   Used Available Use% Mounted on\n"
            "/dev/sdb1      103079200\n")
        self.assertRaises(PersistenceError, factory._parseDiskFreeCommandOutForAvailableSpace, dfOut)
        
    def testNotANumber(self):
        dfOut = (
            "Filesystem     1K-blocks   Used Available Use% Mounted on\n"
            "/dev/sdb1      103079200 245600  NOTANUMBER   1% /home\n")
        self.assertRaises(PersistenceError, factory._parseDiskFreeCommandOutForAvailableSpace, dfOut)

    def testLargeValue(self):
        dfOut = (
            "Filesystem     1K-blocks   Used Available Use% Mounted on\n"
            "/dev/sdb1      103079200 245600  975908240000000000000000   1% /home\n")
        availableSpace = factory._parseDiskFreeCommandOutForAvailableSpace(dfOut)
        self.assertEquals(availableSpace, 999330037760000000000000000)
