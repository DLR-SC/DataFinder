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
Constants definitions of the meta data support. 
"""


from datafinder.core.configuration.properties import constants as const


__version__ = "$Revision-Id:$" 


# Property categories
USER_PROPERTY_CATEGORY = const.USER_PROPERTY_CATEGORY
MANAGED_SYSTEM_PROPERTY_CATEGORY = const.MANAGED_SYSTEM_PROPERTY_CATEGORY
UNMANAGED_SYSTEM_PROPERTY_CATEGORY = const.UNMANAGED_SYSTEM_PROPERTY_CATEGORY
DATAMODEL_PROPERTY_CATEGORY = const.DATAMODEL_PROPERTY_CATEGORY

# System-specific property identifiers
MODIFICATION_DATETIME_ID = const.MODIFICATION_DATETIME_ID
CREATION_DATETIME_ID = const.CREATION_DATETIME_ID
OWNER_ID = const.OWNER_ID
MIME_TYPE_ID = const.MIME_TYPE_ID
DATATYPE_ID = const.DATATYPE_ID
DATASTORE_NAME_ID = const.DATASTORE_NAME_ID
SIZE_ID = const.SIZE_ID
CONTENT_MODIFICATION_DATETIME_ID = const.CONTENT_MODIFICATION_DATETIME_ID
CONTENT_CREATION_DATETIME_ID = const.CONTENT_CREATION_DATETIME_PROPERTY_ID
CONTENT_SIZE_ID = const.CONTENT_SIZE_ID
CONTENT_IDENTIFIER_ID = const.CONTENT_IDENTIFIER_ID
ARCHIVE_RETENTION_EXCEEDED_ID = const.ARCHIVE_RETENTION_EXCEEDED_DATETIME_ID
ARCHIVE_ROOT_COLLECTION_ID = const.ARCHIVE_ROOT_COLLECTION_ID
ARCHIVE_PART_INDEX_ID = const.ARCHIVE_PART_INDEX_ID
ARCHIVE_PART_COUNT_ID = const.ARCHIVE_PART_COUNT_ID
DATA_FORMAT_ID = const.DATA_FORMAT_ID
