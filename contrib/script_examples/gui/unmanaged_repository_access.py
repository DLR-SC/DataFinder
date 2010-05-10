#
# Created: 07.03.2010 schlauch <Tobias.Schlauch>
# Changed: $Id: unmanaged_repository_access.py 4579 2010-03-30 14:22:33Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#
# @title: Hello World!
# @description: Tries to create file "/C:/test.txt".  
# @datatypes:
# @dataformats:
# @icon: The Icon
# @version: 0.0.1
#


""" 
The standard hello world example.
"""


import logging
        
from datafinder.gui.user import script_api
from datafinder.script_api.error import ItemSupportError
from datafinder.script_api.repository import setWorkingRepository
from datafinder.script_api.item.item_support import createLeaf


__version__ = "$LastChangedRevision: 4579 $"

                
_log = logging.getLogger("script")

umr = script_api.unmanagedRepositoryDescription()
if not umr is None:
    setWorkingRepository(umr)
    _log.info(script_api.currentSelection())
    _log.info(script_api.currentCollection())
    
    _log.info("Creating test file test.txt..")
    script_api.lock(["/C:"])
    try:
        createLeaf("/C:/test.txt", dict())
    except ItemSupportError, error:
        _log.error(error.message)
    finally:
        script_api.unlock(["/C:"])
        script_api.selectItem("/C:/test.txt")
else:
    _log.error("Cannot access unmanaged repository.")
