#
# Created: 29.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: constants.py 4626 2010-04-20 20:57:02Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Constant definitions for connection handling.
"""


import re

from webdav.Constants import NS_DAV, PROP_RESOURCE_TYPE

from datafinder.persistence.common import character_constants


__version__ = "$LastChangedRevision: 4626 $"


# Define character sets for names
_firstPropertyChar = character_constants.LETTERS + character_constants.UNDERSCORE
_propertyChar = _firstPropertyChar + character_constants.NUMBER + character_constants.DASH + character_constants.DOT
_firstResourceChar = _firstPropertyChar + character_constants.NUMBER + character_constants.TILDE + character_constants.EXCLAM + \
                     character_constants.DOLLAR + character_constants.DOT + character_constants.DASH + character_constants.PLUS + \
                     character_constants.EQUAL + character_constants.SHARP
_resourceChar = _firstResourceChar + character_constants.SPACE


# Defines regular expressions for name validations
PROPERTYNAME_VALID_STARTCHARACTER_RE = re.compile(u"^["+ _firstPropertyChar +"]")
PROPERTYNAME_INVALID_CHARACTER_RE = re.compile(u"[^"+ _propertyChar +"]")
IDENTIFIER_VALID_STARTCHARACTER_RE = re.compile(u"^["+ _firstResourceChar +"]")
IDENTIFIER_INVALID_CHARACTER_RE = re.compile(u"[^"+ _resourceChar +"]")

# Constants for connection pooling
MAX_POOL_NUMBER = 10
MAX_CONNECTION_NUMBER = 4

# Defines special WebDAV properties
LINK_TARGET_PROPERTY = ("http://dlr.de/system/", "linkTarget")
RESOURCE_TYPE_PROPERTY = (NS_DAV, PROP_RESOURCE_TYPE)
