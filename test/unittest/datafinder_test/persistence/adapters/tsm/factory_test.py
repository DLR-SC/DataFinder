#
# Created: 22.09.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: factory_test.py 4255 2009-09-24 11:24:06Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Contains tests of the TSM factory.
"""


import unittest

from datafinder.persistence.adapters.tsm import factory
from datafinder.persistence.adapters.tsm.data.adapter import DataTsmAdapter
from datafinder.persistence.common.configuration import BaseConfiguration


__version__ = "$LastChangedRevision: 4255 $"


class FileSystemTestCase(unittest.TestCase):
    """ Tests cases of the TSM factory. """
    
    def testCreateDataStorer(self):
        """ Tests the creation of the TSM specific data adaptor. """
        
        tsmFileSystem = factory.FileSystem(BaseConfiguration("tsm://host.de/basePath"))
        self.assertTrue(isinstance(tsmFileSystem.createDataStorer("/logical/Identifier"), DataTsmAdapter))
        
        tsmFileSystem = factory.FileSystem(BaseConfiguration("tsm://host.de/basePath"))
        self.assertTrue(isinstance(tsmFileSystem.createDataStorer("/logical/Identifier"), DataTsmAdapter))
