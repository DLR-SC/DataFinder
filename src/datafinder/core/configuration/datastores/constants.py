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
Implements common constants
"""


__version__ = "$Revision-Id:$" 


DEFAULT_STORE_ICONNAME = "dataStore"

DEFAULT_STORE = "Default Store"
FILE_STORE = "File System Store" 
FTP_STORE = "FTP Store" 
GRIDFTP_STORE = "GridFTP Store"
OFFLINE_STORE = "Off-line Store" 
TSM_CONNECTOR_STORE = "TSM Store"
WEBDAV_STORE = "WebDAV Store"
S3_STORE = "S3 Store"
SUBVERSION_STORE = "Subversion Store"

ARCHIVE_STORE_CATEGORY = (TSM_CONNECTOR_STORE)
ONLINE_STORE_CATEGORY = (DEFAULT_STORE, FILE_STORE, FTP_STORE, GRIDFTP_STORE, 
                         WEBDAV_STORE, S3_STORE, SUBVERSION_STORE)
OFFLINE_STORE_CATEGORY = (OFFLINE_STORE)


# enumeration definitions
class _StorageReailisationModeEnumeration(object):
    """ Defines modes for storage realization. """
    
    FLAT = "Flat"
    HIERARCHICAL = "Hierarchical"

class _SecurityModeEnumeration(object):
    """ Defines GridFTP-specific security modes. """
    
    STANDARD = "Standard"
    PRIVATE = "Private"
    SAFE = "Safe"
    
class _TransferModeEnumeration(object):
    """ Defines GridFTP-specific transfer modes. """
    
    STREAM_MODE = "Stream"
    EXTENDED_MODE = "Extended"

    
GRIDFTP_SECURITY_MODE_ENUM = _SecurityModeEnumeration
GRIDFTP_TRANSFER_MODE_ENUM = _TransferModeEnumeration
STORAGE_REALISATION_MODE_ENUM = _StorageReailisationModeEnumeration
