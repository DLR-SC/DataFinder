#
# Created: 07.04.2009 Michael Meinel
# Changed: $Id: constants.py 4109 2009-05-26 08:48:58Z schlauch $
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


"""
This module provides constants for the L{datafinder.core.item} package.
"""


__version__ = "$LastChangedRevision: 4109 $"


# ItemState -> Indicates whether and how the item is accessible
ITEM_STATE_NULL = "ItemState:NULL"
ITEM_STATE_INACCESSIBLE = "ItemState:INACCESSIBLE"
ITEM_STATE_ACCESSIBLE = "ItemState:ACCESSIBLE"
ITEM_STATE_MIGRATED = "ItemState:MIGRATED"
ITEM_STATE_ARCHIVED = "ItemState:ARCHIVED"
ITEM_STATE_ARCHIVED_READONLY = "ItemState:ARCHIVED_READONLY"
ITEM_STATE_ARCHIVED_MEMBER = "ItemState:ARCHIVED_MEMBER"
ITEM_STATE_UNSUPPORTED_STORAGE_INTERFACE = "ItemState:UNSUPPORTED_STORAGE_INTERFACE"
