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
Definition commonly used character constants mainly used building regular expressions.
"""


import re
import unicodedata


__version__ = "$Revision-Id:$" 


_unicodeUmlaut = [unicodedata.lookup("LATIN CAPITAL LETTER A WITH DIAERESIS"),
                  unicodedata.lookup("LATIN SMALL LETTER A WITH DIAERESIS"),
                  unicodedata.lookup("LATIN CAPITAL LETTER O WITH DIAERESIS"),
                  unicodedata.lookup("LATIN SMALL LETTER O WITH DIAERESIS"),
                  unicodedata.lookup("LATIN CAPITAL LETTER U WITH DIAERESIS"),
                  unicodedata.lookup("LATIN SMALL LETTER U WITH DIAERESIS"),
                  unicodedata.lookup("LATIN SMALL LETTER SHARP S")]
 
# Define characters and character base sets
SPACE = " "
UNDERSCORE = "_"
DASH = "\-"
DOT = "\."
EXCLAM = "\!"
TILDE   = "\~"
DOLLAR  = "\$"
PLUS = "+"
EQUAL = "="
SHARP = "#"
GERMAN_UMLAUTE = u"".join(_unicodeUmlaut)
ALPHABET = "A-Za-z"
NUMBER = "0-9"

# Define character groups
LETTERS = ALPHABET + GERMAN_UMLAUTE

# Define character sets for names
_firstPropertyChar = LETTERS + UNDERSCORE
_propertyChar = _firstPropertyChar + NUMBER + DASH + DOT
_firstResourceChar = _firstPropertyChar + NUMBER + TILDE + EXCLAM + \
                     DOLLAR + DOT + DASH + PLUS + EQUAL + SHARP
_resourceChar = _firstResourceChar + SPACE


# Defines regular expressions for name validations
PROPERTYNAME_VALID_STARTCHARACTER_RE = re.compile(u"^["+ _firstPropertyChar +"]")
PROPERTYNAME_INVALID_CHARACTER_RE = re.compile(u"[^"+ _propertyChar +"]")
IDENTIFIER_VALID_STARTCHARACTER_RE = re.compile(u"^["+ _firstResourceChar +"]")
IDENTIFIER_INVALID_CHARACTER_RE = re.compile(u"[^"+ _resourceChar +"]")
