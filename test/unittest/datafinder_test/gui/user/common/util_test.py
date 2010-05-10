#
# Created: 07.03.2009 mohr_se <steven.mohr@dlr.de>
# Changed: $Id: util_test.py 4077 2009-05-19 14:54:27Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Test for the datafinder.gui.user.common.util module
"""


import unittest, datetime, decimal

from PyQt4 import QtCore

from datafinder.gui.user.common.util import convertToPlainPythonObject, extractPyObject


__version__ = "$LastChangedRevision: 4077 $"


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
