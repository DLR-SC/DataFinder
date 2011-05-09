# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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
This module defines meta data identifiers, display names and descriptions.
"""


__version__ = "$Revision-Id:$" 


# definition of property categories
UNMANAGED_SYSTEM_PROPERTY_CATEGORY = u"____system.unmanaged____"
MANAGED_SYSTEM_PROPERTY_CATEGORY = u"____system.managed____"
DATAMODEL_PROPERTY_CATEGORY = u"____datamodel____"
USER_PROPERTY_CATEGORY = u"____user____" 

# definition of property types
ANY_TYPE = u"Any"
BOOLEAN_TYPE = u"Boolean"
DATETIME_TYPE = u"Date Time"
LIST_TYPE = u"List"
NUMBER_TYPE = u"Number"
STRING_TYPE = u"String"

# definition of property value restrictions
MINIMUM_VALUE = u"minimumValue"
MAXIMUM_VALUE = u"maixmumValue"
MINIMUM_LENGTH = u"minimumLength"
MAXIMUM_LENGTH = u"maximumLength"
MINIMUM_NUMBER_OF_DECIMAL_PLACES = u"minimumNumberOfDecimalPlaces"
MAXIMUM_NUMBER_OF_DECIMAL_PLACES = u"maximumNumberOfDecimalPlaces"
OPTIONS = u"options"
OPTIONS_MANDATORY = u"optionsMandatory"
PATTERN = u"pattern"
ALLOWED_SUB_TYPES = "subTypes"

# definition of property identifiers
MODIFICATION_DATETIME_ID = u"____modificationdatetime____"
CREATION_DATETIME_ID = u"____creationdatetime____"
OWNER_ID = u"____owner____"
MIME_TYPE_ID = u"____mimetype____"
DATATYPE_ID = u"____datatype____"
DATASTORE_NAME_ID = u"____datastorename____"
SIZE_ID = u"____size____"
CONTENT_MODIFICATION_DATETIME_ID = u"____contentmodificationdatetime____"
CONTENT_CREATION_DATETIME_PROPERTY_ID = u"____contentcreationdatetime____"
CONTENT_SIZE_ID = u"____content.size____"
CONTENT_IDENTIFIER_ID = u"____contentidentifier____"
ARCHIVE_RETENTION_EXCEEDED_DATETIME_ID = u"____archiveretentionexceededdatetime____"
ARCHIVE_ROOT_COLLECTION_ID = u"____archiverootcollection____"
ARCHIVE_PART_INDEX_ID = u"____archviepartindex____"
ARCHIVE_PART_COUNT_ID = u"____archivepartcount____"
DATA_FORMAT_ID = u"____dataformat____"

# definition of property display names
MODIFICATION_DATETIME_DISPLAYNAME = u"Modification Date"
CREATION_DATETIME_DISPLAYNAME = u"Creation Date"
SIZE_DISPLAYNAME = u"Size"
OWNER_DISPLAYNAME = u"Owner"
MIME_TYPE_DISPLAYNAME = u"MIME Type"
DATATYPE_DISPLAYNAME = u"Data Type"
DATASTORE_DISPLAYNAME = u"Storage Location"
CONTENT_MODIFICATION_DATETIME_DISPLAYNAME = u"Content Modification Date"
CONTENT_CREATION_DISPLAYNAME = u"Content Creation Date"
CONTENT_SIZE_DISPLAYNAME = u"Content Size"
CONTENT_IDENTIFIER = u"Content Identifier"
ARCHIVE_RETENTION_EXCEEDED_DISPLAYNAME = u"Archive Retention Exceeded Date"
ARCHIVE_ROOT_COLLECTION_DISPLAYNAME = u"Archive Root Collection"
ARCHIVE_PART_INDEX_DISPLAYNAME = u"Archive Sequence Number"
ARCHIVE_PART_COUNT_DISPLAYNAME = u"Archive Parts"
DATA_FORMAT_DISPLAYNAME = u"Data Format"

# definition of property descriptions
MODIFICATION_DATETIME_DESCRIPTION = u"Modification date of the item."
CREATION_DATETIME_DESCRIPTION = u"Creation date of the item."
SIZE_DESCRIPTION = u"Size of the item."
OWNER_DESCRIPTION = u"Owner of the item."
MIME_TYPE_DESCRIPTION = u"MIME type associated with the item."
DATATYPE_DESCRIPTION = u"Data type of the item."
DATASTORE_NAME_DESCRIPTION = u"Logical name of the storage location of the associated document."
CONTENT_MODIFICATION_DATETIME_DESCRIPTION = u"Modification date of the associated content."
CONTENT_CREATION_DATETIME_DESCRIPTION = u"Modification date of the associated content."
CONTENT_SIZE_DESCRIPTION = u"Size of the associated content."
CONTENT_IDENTIFIER_DESCRIPTION = u"Additional identifier on the storage resource."
ARCHIVE_RETENTION_EXCEEDED_DESCRIPTION = u"Date-time when the archive is going to be deleted."
ARCHIVE_ROOT_COLLECTION_DESCRIPTION = u"Root item of an archived collection."
ARCHIVE_PART_INDEX_DESCRIPTION = u"The number of the incremental update that contains this item."
ARCHIVE_PART_COUNT_DESCRIPTION = u"The number of incremental updates this archive consists of."
DATA_FORMAT_DESCRIPTION = u"Determines the format of the data file."
