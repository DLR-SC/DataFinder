# @description: Performs tests using data store "Data Store" and data type "Directory".
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
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
The standard hello world example.
"""


import datetime
import logging
import StringIO
import unicodedata
        
from datafinder.gui.user import script_api as gui_api
from datafinder.script_api.repository import setWorkingRepository
from datafinder.script_api.item import item_support
from datafinder.script_api.properties import constants as const
from datafinder.script_api.properties import property_support
from datafinder.script_api.properties import \
    DomainObject, DomainObjectType, DomainProperty, StringType


__version__ = "$Revision-Id$" 


_DATA_STORE_NAME = "Cloud Store" # Change this to use another data store
# Change this to use another data type
# The data type should allow recursive definitions
_DATA_TYPE_NAME = "Directory" # Change this to use with another data model
_SMALL_AE = unicodedata.lookup("LATIN SMALL LETTER A WITH DIAERESIS")

                
_log = logging.getLogger("script")


class _Author(DomainObject):
    firstName = DomainProperty(StringType(2), None, "First Name", "This is the first name.")
    lastName = DomainProperty(StringType(2), None, "Last Name", "This is the last name.")

    def __init__(self, firstName="", lastName=""):
        DomainObject.__init__(self)
        self.firstName = firstName
        self.lastName = lastName
    
    @firstName.setValidate
    def _validateFirstName(self):
        self._validateName(self.firstName)
    
    @lastName.setValidate
    def _validateLastName(self):
        self._validateName(self.lastName)
    
    @staticmethod
    def _validateName(name):
        if name is None:
            raise ValueError("Name should not be empty.")
        
def _createLeaf():
    for _ in range(3):
        collectionPaths = [u"/test 1" , u"/test 1" + "/sub test"]

        # Create test collection structure and a test file
        for path in collectionPaths: 
            item_support.createCollection(path, {"____datatype____": _DATA_TYPE_NAME})
        
        _log.info("Creating test file test.txt..")
        leafPath = collectionPaths[0] + u"/test"  + ".txt"
        properties = dict()
        properties[const.DATA_FORMAT_ID] = "TEXT"
        properties[const.DATASTORE_NAME_ID] = _DATA_STORE_NAME
        properties[const.CONTENT_MODIFICATION_DATETIME_ID] = datetime.datetime.now()
        properties[const.CONTENT_CREATION_DATETIME_ID] = datetime.datetime.now()
        properties[const.CONTENT_SIZE_ID] = 0
      
        property_support.registerPropertyDefinition("author", DomainObjectType(_Author))
        properties["author"] = _Author("Me", "You" + _SMALL_AE)
        item_support.createLeaf(leafPath, properties)
        
        # Read and write some data
        item_support.storeData(leafPath, StringIO.StringIO("test..."))
        _log.info(item_support.retrieveData(leafPath).read())
        
        # Tests link creation and access
        linkPath = collectionPaths[0] + "/leaf_link.txt"
        item_support.createLink(linkPath, leafPath)
        
        # Read and write some properties
        properties = {
            "string": "string", "date": datetime.datetime.now(),
            "boolean": True, "number": 10.7, 
            "list": ["string", 10, True, datetime.datetime.now()]}
        property_support.storeProperties(leafPath, properties)
        _log.info(property_support.retrieveProperties(leafPath))
        
        # Copy and move it
        copiedLeafPath = collectionPaths[1] + "/test.txt"
        item_support.copy(leafPath, copiedLeafPath)
        _log.info(item_support.retrieveData(copiedLeafPath).read())
        movedLeafPath = collectionPaths[1] + "/test_2.txt"
        item_support.move(leafPath, movedLeafPath)
        _log.info(item_support.retrieveData(movedLeafPath).read())
        
        # Delete created collections/files
        item_support.delete(collectionPaths[0])

def _cb():
    gui_api.unlock(["/"])
    gui_api.selectItem("/test.txt")

mr = None
mr = gui_api.managedRepositoryDescription()
if not mr is None:
    setWorkingRepository(mr)
    _log.info(gui_api.currentSelection())
    _log.info(gui_api.currentCollection())
    
    
    gui_api.lock(["/"])
   
    gui_api.performWithProgressDialog(_createLeaf, _cb)
else:
# remove comments to execute on command line and comment line 146 and 164    
#    from datafinder.script_api import repository
#    repo = repository.connectRepository("somerepository/data", 
#                                        "somerepository/config", "username", "password")
#
#    _createLeaf()
    
    _log.error("Please connect the shared repository.")
    
