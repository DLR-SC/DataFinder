# $Filename$$
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
Tests the repository path filter.
"""


import unittest

from datafinder.gui.user.models.repository.filter.path_filter import PathFilter
from datafinder_test.gui.user.mocks import BaseRepositoryMock, BaseItemMock


__version__ = "$Revision-Id:$" 


class PathFilterTest(unittest.TestCase):
    """ Tests of the repository path filter """

    def setUp(self):
        """ Creates the repository and the filter. """
        
        self._items = [BaseItemMock("/test/another"), BaseItemMock("/jepp/here")]
        self._repositoryModel = BaseRepositoryMock(self._items)
        self._pathFilter = PathFilter(self._repositoryModel)

        # Checking number of children of the root index
        self.assertEquals(self._repositoryModel.rowCount(), 2) 
        self.assertEquals(self._pathFilter.rowCount(), 0) 
        
    def testFiltering(self):
        """ Tests the different filter cases. """
        
        # Restrict to the first item
        self._pathFilter.item = self._items[0]
        self.assertEquals(self._pathFilter.rowCount(), 1)
        index = self._pathFilter.indexFromPath("/test")
        self.assertEquals(self._pathFilter.nodeFromIndex(index).path, "/test")
        
        # Restrict to the second item
        self._pathFilter.item = self._items[1]
        self.assertEquals(self._pathFilter.rowCount(), 1)
        index = self._pathFilter.indexFromPath("/jepp")
        self.assertEquals(self._pathFilter.nodeFromIndex(index).path, "/jepp")
        
        # Restrict to a non-existing item
        self._pathFilter.item = BaseItemMock("/unknown")
        self.assertEquals(self._pathFilter.rowCount(), 0)
        
        # Restrict to "None"
        self._pathFilter.item = None
        self.assertEquals(self._pathFilter.rowCount(), 0)
