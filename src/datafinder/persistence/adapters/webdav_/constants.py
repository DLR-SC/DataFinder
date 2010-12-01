# $Filename$ 
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
Constant definitions for connection handling.
"""


import re

from webdav.Constants import NS_DAV, PROP_RESOURCE_TYPE

from datafinder.persistence.common import character_constants


__version__ = "$Revision-Id:$" 


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
