# $Filename$ 
# pylint: disable=C0103,W1010
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#
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
Operating system independent start script (Win32 and UN*X)
for the DataFinder application.
"""


import os
import locale
import sys

from datafinder.gui.user import application


__version__ = "$Revision-Id:$" 


dfStart = os.environ.get("DF_START")
profile = os.environ.get("DF_PROFILE")
debug = os.environ.get("DF_DEBUG")

# set the encoding
encoding = "UTF-8"
if not locale.getdefaultlocale()[1] is None:
    encoding = locale.getdefaultlocale()[1]
try:
    sys.setdefaultencoding(encoding)
except AttributeError:
    if sys.getdefaultencoding() == "ascii":
        print("It is required to correctly set default encoding. " + \
              "Please see site.py for further details.")
    
if profile:
    import cProfile
    cProfile.run("application.main()", sort="cumulative")
else:
    application.main(dfStart, bool(debug))
