# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2013, German Aerospace Center (DLR)
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
#
# @title: Directory Importer
# @description: Imports a directory structure.  
#


""" 
Importing directory structure.
"""


from logging import getLogger

from datafinder.core.configuration.properties.constants import DATATYPE_ID, DATASTORE_NAME_ID
from datafinder.gui.user import script_api as gui_api
from datafinder.script_api.error import ItemSupportError
from datafinder.script_api.item import item_support
from datafinder.script_api.repository import setWorkingRepository


__version__ = "$LastChangedRevision: 59 $"


_DATASTORE_DEFAULT_VALUE = "DataStore" # Data store in which files are imported 
_DATATYPE_DEFAULT_VALUE = "Directory" # Data type name of newly imported directories
            

logger = getLogger()
targetRepository = gui_api.managedRepositoryDescription()
targetPath = gui_api.getScriptExecutionContext().itemPaths[0]

sourceRepository = gui_api.unmanagedRepositoryDescription()
setWorkingRepository(sourceRepository)
sourcePath = gui_api.currentCollection()


def _determinePropertiesCallback(itemDescription):
    """ Determines the properties for the given item. 
    This callback is called for every imported item. Thus, you can
    implement a more specific property assignment.
    """

    logger.info(itemDescription)
    properties = dict()
    if itemDescription.isLeaf:
        properties[DATASTORE_NAME_ID] = _DATASTORE_DEFAULT_VALUE
    else:
        if not DATATYPE_ID in properties:
            properties[DATATYPE_ID] = _DATATYPE_DEFAULT_VALUE
    return properties
    
    
def _worker():
    """ Performs the import. """

    try:
        item_support.performImport(sourcePath, targetPath, targetRepository, 
                                   dict(), True, True, _determinePropertiesCallback)
    except ItemSupportError, error:
        logger.error(error.message)


def _workerCallback():
    """ Unlocks target path when work is done. """
    
    gui_api.unlock([targetPath], targetRepository)


sourcePath = gui_api.getExistingCollection(sourceRepository, helpText="Please select the collection you want to import.")
if not sourcePath is None:
    gui_api.lock([targetPath], targetRepository)
    gui_api.performWithProgressDialog(_worker, _workerCallback, "Import Directory", "Performing the directory import...")
