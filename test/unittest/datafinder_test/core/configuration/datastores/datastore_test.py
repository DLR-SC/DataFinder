#
# Created: 08.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: datastore_test.py 4560 2010-03-23 15:52:44Z ney_mi $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements test cases for the concrete data store configurations. 
"""


from copy import copy, deepcopy
import unittest

from datafinder.core.configuration.datastores import datastore
from datafinder.core.configuration.gen import datastores

__version__ = "$LastChangedRevision: 4560 $"


class DefaultDataStoreTestCase(unittest.TestCase):
    """ Tests the default data store configuration. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._store = datastore.DefaultDataStore()
        
    def testToPersistenceRepresentation(self):
        """ Tests the persistence representation creation. """
        
        self._store.name = "name"
        self._store.storeType = "Default Store"
        self._store.iconName = "New Icon"
        self._store.isDefault = True
        self._store.owner = "TheOwner"
        
        persistenceRepresentation = self._store.toPersistenceRepresentation()
        
        self.assertEquals(self._store.name, persistenceRepresentation.name)
        self.assertEquals(self._store.storeType, persistenceRepresentation.storeType)
        self.assertEquals(self._store.iconName, persistenceRepresentation.iconName)
        self.assertEquals(self._store.isDefault, persistenceRepresentation.isDefault)
        self.assertEquals(self._store.owner, persistenceRepresentation.owner)

    def testCopying(self):
        """ Tests the copying behavior. """
        
        self._store.name = "name"
        self._store.storeType = "Default Store"
        self._store.iconName = "New Icon"
        self._store.isDefault = True
        self._store.owner = "TheOwner"
        
        for copyFunction in [copy, deepcopy]:
            copy_ = copyFunction(self._store)
            
            self.assertEquals(self._store.name, copy_.name)
            self.assertEquals(self._store.storeType, copy_.storeType)
            self.assertEquals(self._store.iconName, copy_.iconName)
            self.assertEquals(self._store.isDefault, copy_.isDefault)
            self.assertEquals(self._store.owner, copy_.owner)
            
            copy_.name = "cp_name"
            copy_.storeType = "cp_Default Store"
            copy_.iconName = "cp_New Icon"
            copy_.isDefault = False
            copy_.owner = "cp_TheOwner"
            
            self.assertNotEquals(self._store.name, copy_.name)
            self.assertNotEquals(self._store.storeType, copy_.storeType)
            self.assertNotEquals(self._store.iconName, copy_.iconName)
            self.assertNotEquals(self._store.isDefault, copy_.isDefault)
            self.assertNotEquals(self._store.owner, copy_.owner)

    def testComparison(self):
        """ Tests the comparison of two instances. """
        
        self.assertEquals(self._store, self._store)
        self.assertEquals(self._store, datastore.DefaultDataStore(self._store.name))
        
        self.assertNotEquals(self._store, datastore.DefaultDataStore("anotherName"))
        self.assertNotEquals(self._store, None)
        

class GridFtpDataStoreTestCase(unittest.TestCase):
    """ Test cases for the GridFTP data store configuration. """

    def setUp(self):
        """ Creates object under test. """
        
        self._store = datastore.GridFtpDataStore()
        
    def testTcpBufferSize(self):
        """ Tests setting the TCP buffer size. """
        
        self._store.tcpBufferSize = 10
        self._store.tcpBufferSize = 60
        
        try:
            self._store.tcpBufferSize = 0
            self.fail("ValueError not raised.")
        except ValueError:
            self.assertTrue(True)
        try:
            self._store.tcpBufferSize = None
            self.fail("ValueError not raised.")
        except ValueError:
            self.assertTrue(True)
        try:
            self._store.tcpBufferSize = "test"
            self.fail("ValueError not raised.")
        except ValueError:
            self.assertTrue(True)
        
    def testParallelConnections(self):
        """ Tests setting parallel connection property. """
        
        self._store.parallelConnections = 0
        self.assertEquals(self._store.parallelConnections, 0)
        self._store.parallelConnections = 10
        self.assertEquals(self._store.parallelConnections, 10)
        self._store.parallelConnections = 60
        self.assertEquals(self._store.parallelConnections, 60)
        
        try:
            self._store.parallelConnections = -1
            self.fail("ValueError not raised.")
        except ValueError:
            self.assertTrue(True)
        try:
            self._store.tcpBufferSize = None
            self.fail("ValueError not raised.")
        except ValueError:
            self.assertTrue(True)
        try:
            self._store.tcpBufferSize = "test"
            self.fail("ValueError not raised.")
        except ValueError:
            self.assertTrue(True)
        

class WebdavDataStoreTestCase(unittest.TestCase):
    """ Test cases for the WebDAV data store configuration. """

    def setUp(self):
        """ Creates object under test. """
        
        self._store = datastore.WebdavDataStore(datastores.webdav())

    def testPassword(self):
        """ Tests the setting of the password. """
        
        self._store.password = "test"
        self.assertEquals(self._store.password, "test")
        self.assertNotEquals(self._store.toPersistenceRepresentation().password, "test")

        self._store.password = None
        self.assertEquals(self._store.password, None)
        
        try:
            self._store.password = 899
            self.fail("ValueError not raised.")
        except ValueError:
            self.assertTrue(True)
        self.assertEquals(self._store.password, None)
        
        
class S3DataStoreTestCase(unittest.TestCase):
    """ Test cases for the WebDAV data store configuration. """

    def setUp(self):
        """ Creates object under test. """
        
        self._store = datastore.S3DataStore(datastores.s3())
    
    def testPassword(self):
        """ Tests the setting of the password. """
        
        self._store.password = "test"
        self.assertEquals(self._store.password, "test")
        self.assertNotEquals(self._store.toPersistenceRepresentation().password, "test")
        