# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:
#
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
Defines interface and default implementation for meta-data-related actions.
"""


__version__ = "$Revision-Id:$" 


class NullMetadataStorer(object):
    """ 
    Null pattern / default implementation of the meta-data-related interface.
    
    @note: Real implementations of this interface are raising errors of
           type L{PersistenceError<datafinder.persistence.error.PersistenceError>}
           to indicate problems.
    """
    
    def __init__(self, identifier):
        """ 
        Constructor. 
        
        @param identifier: The logical identifier of the associated item. 
                           This is usually the path relative to a root.
        @type identifier: C{unicode}
        """
        
        self.identifier = identifier
    
    def retrieve(self, propertyIds=None):
        """ 
        Retrieves all meta data associated with the item.
        C{propertyIds} allows explicit selection of meta data.
        
        @return: Meta data of the associated item.
        @rtype: C{dict} of C{unicode}, L{MetadataValue<datafinder.common.metadata.
        value_mapping.MetaddataValue>}
        """
        
        self, propertyIds = self, propertyIds # silent pylint
        return dict()

    def update(self, properties):
        """ 
        Update the associated meta data. 
        Adds new properties or updates existing property values. 
        
        @param properties: New / updated meta data.
        @type properties: C{dict} of C{unicode}, C{object}
        """
        
        pass
    
    def delete(self, propertyIds):
        """
        Deletes the selected meta data.
        
        @param propertyIds: Specifies the meta data that has to be deleted.
        @type propertyIds: C{list} of C{unicode} 
        """
        
        pass
    
    def search(self, restrictions):
        """ 
        Allows searching for items based on meta data restrictions.
        
        @param restrictions: Boolean conjunction of meta data restrictions.
                             For defined search operators see L{datafinder.persistence.constants}.
        @type restrictions: C{list}
        
        @return: List of matched item identifiers.
        @rtype: C{list} of C{unicode}
        """
        
        self, restrictions = self, restrictions # silent pylint
        return list()
