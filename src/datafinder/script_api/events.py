# $Filename$$
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
Module to enable registering for events within DataFinder core
"""


from datafinder.core import events
from datafinder.script_api.error import ScriptApiError


__version__ = "$Revision-Id:$" 


#Constants defining the events 
IMPORT_EVENT = "ImportEvent"


#mapping events to classes
_eventMap = {IMPORT_EVENT: events.ImportEvent()}


def registerListener(event, callback):
    """ Register for an event 
    
    @raise ScriptApiError: If the event is not supported.
    """
    
    _getEvent(event).register(callback)


def unregisterListener(event, callback):
    """ Unregister the event 
    
    @raise ScriptApiError: If the event is not supported
                           or the function has not formerly been registered.
    """

    try:
        _getEvent(event).unregister(callback)
    except ValueError:
        raise ScriptApiError()


def _getEvent(identifier):
    """ Retrieves event class for the given ID and 
    raises a ScriptError if an corresponding event 
    cannot be found. """
    
    try:
        return _eventMap[identifier]
    except KeyError:
        raise ScriptApiError("The event '%s' does not exist." % identifier)
