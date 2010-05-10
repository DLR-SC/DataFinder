#
# Created: 13.01.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: constants.py 4626 2010-04-20 20:57:02Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines a set of commonly used constants.
"""


import re

from datafinder.persistence.common import character_constants


__version__ = "$LastChangedRevision: 4626 $"


_firstIdentifierCharacters = character_constants.LETTERS + character_constants.UNDERSCORE + character_constants.NUMBER + \
                             character_constants.TILDE + character_constants.EXCLAM + \
                             character_constants.DOLLAR + character_constants.DOT + character_constants.DASH + character_constants.PLUS + \
                             character_constants.EQUAL + character_constants.SHARP
_identifierCharacters = _firstIdentifierCharacters + character_constants.SPACE

IDENTIFIER_VALID_FIRSTCHARACTER_RE = re.compile(u"^["+ _firstIdentifierCharacters +"]")
IDENTIFIER_INVALID_CHARACTER_RE = re.compile(u"[^"+ _identifierCharacters +"]")
