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
Test for the datafinder.gui.user.common.util module
"""


import unittest, datetime, decimal

from PyQt4 import QtCore

from datafinder.gui.user.common.util import convertToPlainPythonObject, extractPyObject


__version__ = "$Revision-Id:$" 


class UtilTestCase(unittest.TestCase): 
    """ Tests the utility module."""
    
    def testConvertToPlainPython(self):
        """ Tests the convertToPlainPythonObject function. """
        
        qString = QtCore.QString(u'test string')
        self.assertTrue(convertToPlainPythonObject(qString) == u'test string') 
        self.assertTrue(type(convertToPlainPythonObject(qString)) == unicode)
        
        self.assertTrue(convertToPlainPythonObject(4.0) == 4.0) 

        qDateTime = QtCore.QDateTime(datetime.datetime(1970, 11, 11, 11, 11))
        self.assertTrue(convertToPlainPythonObject(qDateTime) == datetime.datetime(1970, 11, 11, 11, 11)) 
        self.assertTrue(type(convertToPlainPythonObject(qDateTime)) == datetime.datetime)
        
    def testExtractPyObject(self):
        """ Tests the extractPyObject function. """
        
        qVariantString = QtCore.QVariant(QtCore.QString(u'test string'))
        self.assertTrue(extractPyObject(qVariantString) == u'test string')
        
        qVariantDouble = QtCore.QVariant(4.05)
        self.assertTrue(extractPyObject(qVariantDouble) == decimal.Decimal("4.05"))
        
        qVariantBool = QtCore.QVariant(True)
        self.assertTrue(extractPyObject(qVariantBool) == True)
        
        qVariantDateTime = QtCore.QVariant(QtCore.QDateTime(datetime.datetime(1970, 11, 11, 11, 11)))
        extractedDatetime = extractPyObject(qVariantDateTime)
        self.assertEquals(extractedDatetime.timetuple()[:-1], datetime.datetime(1970, 11, 11, 11, 11).timetuple()[:-1])
        
        qVariantList = QtCore.QVariant(["test1", 33, "test2", 76])
        self.assertTrue(extractPyObject(qVariantList) == ["test1", 33, "test2", 76])
        
        qVariantLong = QtCore.QVariant(30000L)
        converted = extractPyObject(qVariantLong)
        self.assertTrue(converted == 30000L)
        
        qVariantInt = QtCore.QVariant(42)
        converted = extractPyObject(qVariantInt)
        self.assertTrue(converted == 42)
        
        qVariantDate = QtCore.QVariant(QtCore.QDate(datetime.date(2004, 2, 2)))
        self.assertTrue(extractPyObject(qVariantDate) == datetime.date(2004, 2, 2))
