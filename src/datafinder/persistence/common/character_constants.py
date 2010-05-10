#
# Created: 13.01.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: character_constants.py 4387 2010-01-13 16:55:06Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Definition commonly used character constants mainly used building regular expressions.
"""


import unicodedata


__version__ = "$LastChangedRevision: 4387 $"


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
GERMAN_UMLAUTS = u"".join(_unicodeUmlaut)
ALPHABET = "A-Za-z"
NUMBER = "0-9"
ALPHABET_WITH_NUMBER = ALPHABET + NUMBER

# Define character groups
LETTERS_WITH_NUMBER = ALPHABET_WITH_NUMBER + GERMAN_UMLAUTS
LETTERS = ALPHABET + GERMAN_UMLAUTS
