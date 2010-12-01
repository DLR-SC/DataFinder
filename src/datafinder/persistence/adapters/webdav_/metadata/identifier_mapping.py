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
This module is intended to hold the mapping of the logical meta data identifiers used
in the DataFinder core package to storage technology specific (here: WebDAV) persistence identifiers.
In later DataFinder versions this is going to be moved to an external configuration file.
"""


from webdav import Constants

from datafinder.persistence.metadata import constants


__version__ = "$Revision-Id:$" 


# the logical system-specific identifiers are mapped to WebDAV-specific counterparts consisting of name space, name pairs  
_davNamespace = Constants.NS_DAV
_datafinderNamespace = "http://dlr.de/"

_logicalToPersistenceIdMapping = dict()
_logicalToPersistenceIdMapping[constants.MODIFICATION_DATETIME] = (_davNamespace, Constants.PROP_LAST_MODIFIED)
_logicalToPersistenceIdMapping[constants.CREATION_DATETIME] = (_davNamespace, Constants.PROP_CREATION_DATE)
_logicalToPersistenceIdMapping[constants.OWNER] = (_davNamespace, Constants.PROP_OWNER)
_logicalToPersistenceIdMapping[constants.MIME_TYPE] = (_davNamespace, Constants.PROP_CONTENT_TYPE)
_logicalToPersistenceIdMapping[constants.SIZE] = (_davNamespace, Constants.PROP_CONTENT_LENGTH)
 
_persistenceToLogicalIdMapping = dict([[value, key] for key, value in _logicalToPersistenceIdMapping.iteritems()])
    

def mapMetadataId(logicalId):
    """ 
    Maps logical identifiers to persistence identifiers. 
    
    @param logicalId: Interface property identifier, i.e. just a name.
    @type logicalId: C{unicode}
    """
    
    try:
        persistenceId = _logicalToPersistenceIdMapping[logicalId]
    except KeyError:
        persistenceId = (_datafinderNamespace, logicalId)
    return persistenceId


def mapPersistenceMetadataId(persistenceId):
    """ 
    Maps persistence identifiers to logical identifiers. 
    
    @param persistenceId: WebDAV-Specific identifier of a property, i.e. a namespace, name pair.
    @type persistenceId: C{tuple} of C{unicode}, C{unicode}
    
    @return: Interface property identifier, i.e. just a name.
    @rtype: C{unicode}
    """
    
    logicalId = None
    try:
        logicalId = _persistenceToLogicalIdMapping[persistenceId]
    except KeyError:
        if persistenceId[0] == _datafinderNamespace:
            logicalId = persistenceId[1]
    return logicalId
