# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
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
The standard hello world example.
"""


import logging
        
from datafinder.gui.user import script_api
from datafinder.script_api.error import ItemSupportError
from datafinder.script_api.repository import setWorkingRepository
from datafinder.script_api.item.item_support import createLeaf


__version__ = "$Revision-Id:$" 

                
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
