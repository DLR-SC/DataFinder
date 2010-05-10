#
# Created: 07.03.2010 schlauch <Tobias.Schlauch>
# Changed: $Id: managed_repository_access.py 4579 2010-03-30 14:22:33Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#
# @title: Hello World!
# @description: Tries to create file "/test.txt" using data store "Data Store".  
# @datatypes:
# @dataformats:
# @icon: The Icon
# @version: 0.0.1
#


""" 
The standard hello world example.
"""


import datetime
import logging
        
from datafinder.gui.user import script_api
from datafinder.script_api.error import ItemSupportError
from datafinder.script_api.repository import setWorkingRepository
from datafinder.script_api.item.item_support import createLeaf


__version__ = "$LastChangedRevision: 4579 $"

                
_log = logging.getLogger("script")

mr = script_api.managedRepositoryDescription()
if not mr is None:
    setWorkingRepository(mr)
    _log.info(script_api.currentSelection())
    _log.info(script_api.currentCollection())
    
    _log.info("Creating test file test.txt..")
    script_api.lock(["/"])
    def _createLeaf():
        properties = dict()
        properties["____dataformat____"] = "TEXT"
        properties["____datastorename____"] = "Data Store"
        properties["____contentmodificationdatetime____"] = datetime.datetime.now()
        properties["____contentcreationdatetime____"] = datetime.datetime.now()
        properties["____content.size____"] = 0
        
        try:
            createLeaf("/test.txt", properties)
        except ItemSupportError, error:
            _log.error(error.message)
    def _cb():
        script_api.unlock(["/"])
        script_api.selectItem("/test.txt")
    script_api.performWithProgressDialog(_createLeaf, _cb)
else:
    _log.error("Please connect the shared repository.")
