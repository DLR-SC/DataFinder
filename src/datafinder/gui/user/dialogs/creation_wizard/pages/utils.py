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
Provides some general functionalities commonly used by different pages.
"""


__version__ = "$Revision-Id:$" 


def determineTargetDataTypes(baseRepositoryModel, index):
    """ Determines the target data types for the given index. """
    
    targetDataTypes = list()
    item = baseRepositoryModel.nodeFromIndex(index)
    repository = baseRepositoryModel.repository
    dataTypeName = None
    
    if not item.dataType is None:
        dataTypeName = item.dataType.name
    if not dataTypeName is None or item.isRoot:
        targetDataTypes = repository.configuration.getTargetDataTypes(dataTypeName)
    return targetDataTypes


def dataTypesCompatible(baseRepositoryModel, sourceIndex, targetIndex):
    """ Determines whether a connection from source index to the target index is defined in the data model. """
    
    source = baseRepositoryModel.nodeFromIndex(targetIndex)
    target = baseRepositoryModel.nodeFromIndex(sourceIndex)
    repository = baseRepositoryModel.repository
    sourceDataTypeName = None
    
    if not source.dataType is None:
        sourceDataTypeName = source.dataType.name
    targetDataTypeName = None
    if not target.dataType is None:
        targetDataTypeName = target.dataType.name
    try:
        result = repository.configuration.existsConnection(sourceDataTypeName, targetDataTypeName)
    except AttributeError:
        result = True
    return result
