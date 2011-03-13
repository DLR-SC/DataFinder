# pylint: disable=R0904
# R0904: pylint warns about too many public methods (>30). 
# However, the methods used for read-only access to attributes are counted as well.
# So it is fine to disable this warning..
# 
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
Provides file storer implementation allowing access to an item on a specific storage system.
"""


import os

from tempfile import NamedTemporaryFile, mkstemp
from datafinder.persistence.error import PersistenceError
        

__version__ = "$Revision-Id:$" 


_BLOCK_SIZE = 30000


class FileStorer(object):
    """ 
    Convenience object provided to allow access of the complete interface. 
    
    @note: All methods of this interface are raising errors of
           type L{PersistenceError<datafinder.persistence.error.PersistenceError>}
           to indicate problems.
    """
    
    def __init__(self, fileSystem, identifier, dataStorer, metadataStorer, privilegeStorer):
        """ 
        Constructor. 
        
        @param fileSystem: File system representation this item belongs to.
        @type fileSystem: L{FileSystem<datafinder.persistence.factory.FileSystem>}
        
        @param dataStorer: Encapsulates data / file system hierarchy specific behavior.
        @type dataStorer: C{object} implementing the interface of L{NullDataStorer<datafinder.
                          persistence.data.datastorer.NullDataStorer>}
        @param metadataStorer: Encapsulates meta data specific behavior.
        @type metadataStorer: C{object} implementing the interface of L{NullMetadataStorer<datafinder.
                              persistence.metadata.metadatastorer.NullMetadataStorer>}
        @param privilegeStorer: Encapsulates privilege specific behavior.
        @type privilegeStorer: C{object} implementing the interface of L{NullPrivilegeStorer<datafinder.
                               persistence.privileges.privilegestorer.NullPrivilegeStorer>}
        """
        
        self.__fileSystem = fileSystem
        self.__identifier = identifier
        self.__dataStorer = dataStorer
        self.__metadataStorer = metadataStorer
        self.__privilegeStorer = privilegeStorer
        self._tempfile = None
        
    @property
    def identifier(self):
        """ Simple getter for the identifier attribute. """
        
        return self.__identifier

    @property
    def uri(self):
        """ Determines the URI of the item. """
        
        result = None
        baseUri = self.__fileSystem.baseUri
        if not baseUri is None and not self.__identifier is None and len(self.__identifier) > 0:
            if baseUri.endswith("/"):
                result = baseUri + self.__identifier[1:]
            else:
                result = baseUri + self.__identifier
            if result.endswith("/"):
                result = result[:-1]
        return result
    
    @property
    def name(self):
        """ Returns the name component of the identifier. """
        
        result = ""
        if not self.__identifier is None:
            result = self.__identifier.rsplit("/")[-1]
        return result
        
    @property
    def fileSystem(self):
        """ Simple getter for the fileSystem attribute. """
        
        return self.__fileSystem
    
    @property
    def dataStorer(self):
        """ Simple getter for the dataStorer attribute. """
        
        return self.__dataStorer
    
    @property
    def metadataStorer(self):
        """ Simple getter for the metadataStorer attribute. """
        
        return self.__metadataStorer
    
    @property
    def privilegeStorer(self):
        """ Simple getter for the privilegeStorer attribute. """
        
        return self.__privilegeStorer
    
    @property
    def parent(self):
        """ Returns the parent file storer. """
        
        identifier = self.__identifier or ""
        parentId = "/".join(identifier.rsplit("/")[:-1])
        if parentId == "" and identifier.startswith("/") and identifier != "/":
            parentId = "/"
        return self.__fileSystem.createFileStorer(parentId)
    
    @property
    def linkTarget(self):
        """ 
        Returns a file storer representing the target the link is pointing to.
        If the file storer is no link the property is C{None}.
        """
        
        if not self.__dataStorer.linkTarget is None:
            return self.__fileSystem.createFileStorer(self.__dataStorer.linkTarget)
    
    @property
    def isLink(self):
        """
        Determines whether the associated item is a symbolic link or not.
        If it is a link the link target can be retrieved using the C{getChildren} method.
        
        @return: Flag indicating whether it is a link or not.
        @rtype: C{bool}
        """
        
        return self.__dataStorer.isLink
    
    @property
    def isCollection(self):
        """
        Determines whether the associated item is an item container or not.
        
        @return: Flag indicating whether it is an item container or not.
        @rtype: C{bool}
        """
        
        return self.__dataStorer.isCollection
    
    @property
    def isLeaf(self):
        """
        Determines whether the associated item is a leaf node or not.
        
        @return: Flag indicating whether it is a leaf node or not.
        @rtype: C{bool}
        """
        
        return self.__dataStorer.isLeaf
     
    @property
    def canAddChildren(self):
        """
        Determines whether it is possible to add new items below this item.
        
        @return: Flag indicating the possibility of adding new items below.
        @rtype: C{bool}
        """
           
        return self.__dataStorer.canAddChildren
        
    def createCollection(self, recursively=False):
        """ 
        Creates a collection. 
        
        @param recursively: If set to C{True} all missing collections are created as well.
        @type recursively: C{bool}
        """
        
        self.__dataStorer.createCollection(recursively)
    
    def createResource(self):
        """ Creates a resource. """
    
        self.__dataStorer.createResource()
    
    def createLink(self, destination):
        """ 
        Creates a symbolic link to the specified destination.
        
        @param destination: Identifies the item that the link is pointing to.
        @type destination: L{FileStorer<datafinder.persistence.factory.FileStorer>
        """
        
        self.__dataStorer.createLink(destination.dataStorer)
    
    def getChildren(self):
        """ 
        Retrieves the logical identifiers of the child items. 
        In case of a symbolic link the identifier of the link target is returned.
        
        @return: List of the child item identifiers.
        @rtype: C{list} of L{FileStorer<datafinder.persistence.factory.FileStorer>}
        """
        
        result = list()
        for item in self.__dataStorer.getChildren():
            result.append(self.__fileSystem.createFileStorer(item))
        return result
    
    def getChild(self, name):
        """ 
        Returns a child for the given name without regarding the resource
        type or existence of the parent item.
        """
        
        if not self.__identifier.endswith("/"):
            identifier = self.__identifier + "/" + name
        else:
            identifier = self.__identifier + name
        return self.__fileSystem.createFileStorer(identifier) 
    
    def exists(self):
        """ 
        Checks whether the item does already exist.
        
        @return: Flag indicating the existence of the item.
        @rtype: C{bool}
        """
        
        return self.__dataStorer.exists()
    
    def delete(self):
        """ Deletes the item. """
        
        self.__dataStorer.delete()
    
    def copy(self, destination):
        """ 
        Copies the associated item.
        
        @param destination: Identifies the moved item.
        @type destination: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        """
        
        self.__dataStorer.copy(destination.dataStorer)
    
    def move(self, destination):
        """ 
        Moves the associated item.
        
        @param destination: Identifies the moved item.
        @type destination: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        """
        
        self.__dataStorer.move(destination.dataStorer)
    
    def readData(self):
        """ 
        Returns the associated data.
        
        @return: Associated data.
        @rtype: C{object} implementing the file protocol.
        """
        
        return self.__dataStorer.readData()
    
    def writeData(self, data):
        """ 
        Writes data of the associated item.
        
        @param data: Associated data.
        @type data: C{object} implementing the file protocol.
        """
        
        self.__dataStorer.writeData(data)
        
    def getTemporaryFileObject(self, fileNameSuffix="", deleteOnClose=True):
        """ 
        Returns a named local temporary file object allowing access to the binary 
        content. The file path of the 
        
        @param deleteOnClose: Automatically deletes the temporary file object when its closed. Default: C{True}
        @type deleteOnClose: C{bool}
        @param fileNameSuffix: Optional suffix for the name of the temporary file. Default: Empty string
        @type fileNameSuffix: C{unicode}
        
        @return: Tuple consisting of local file path and opened temporary file object.
        @rtype: C{tuple} of C{unicode}, C{object} implementing file protocol
        
        @raise PersistenceError: Indicating problems accessing file content.
        """
        
        if self._tempfile is None \
        or not os.path.exists(self._tempfile[0]):
            inStream = self.readData()
            try:
                if deleteOnClose:
                    tempNamedFile = NamedTemporaryFile(suffix=fileNameSuffix)
                    path = tempNamedFile.name
                    fileHandle = tempNamedFile.file
                else:
                    fd, path = mkstemp(suffix=fileNameSuffix)
                    fileHandle = os.fdopen(fd, "w+b")

                block = inStream.read(_BLOCK_SIZE)
                while len(block) > 0:
                    fileHandle.write(block)
                    block = inStream.read(_BLOCK_SIZE)
                    while len(block) > 0:
                        fileHandle.write(block)
                        block = inStream.read(_BLOCK_SIZE)
            except (OSError, IOError), error:
                reason = os.strerror(error.errno or 0)
                errorMessage = "Cannot create local temporary file for '%s'. Reason: '%s'." % (self.identifier, reason)
                raise PersistenceError(errorMessage)
            finally:
                inStream.close()
            self._tempfile = path, fileHandle
        elif self._tempfile is not None:
            self._tempfile = self._tempfile[0], open(self._tempfile[0], "r+b")
        return self._tempfile
        
    def retrieveMetadata(self, propertyIds=None):
        """ 
        Retrieves all meta data associated with the item.
        C{propertyIds} allows explicit selection of meta data.
        
        @return: Meta data of the associated item.
        @rtype: C{dict} of C{unicode}, L{MetadataValue<datafinder.common.metadata.
        value_mapping.MetaddataValue>}
        """
        
        return self.__metadataStorer.retrieve(propertyIds)

    def updateMetadata(self, properties):
        """ 
        Update the associated meta data. 
        Adds new properties or updates existing property values. 
        
        @param properties: New / updated meta data.
        @type properties: C{dict} of C{unicde}, C{object}
        """
        
        self.__metadataStorer.update(properties)
    
    def deleteMetadata(self, propertyIds):
        """
        Deletes the selected meta data.
        
        @param propertyIds: Specifies the meta data that has to be deleted.
        @type propertyIds: C{list} of C{unicode} 
        """
        
        self.__metadataStorer.delete(propertyIds)
    
    def metadataSearch(self, restrictions):
        """ 
        Allows searching for items based on meta data restrictions.
        
        @param restrictions: Boolean conjunction of meta data restrictions.
                             For defined search operators see L{datafinder.persistence.constants}.
        @type restrictions: C{list}
        
        @return: List of matched item identifiers.
        @rtype: C{list} of L{FileStorer<datafinder.persistence.factory.FileStorer>}
        """
        
        result = list()
        for item in self.__metadataStorer.search(restrictions):
            result.append(self.__fileSystem.createFileStorer(item))
        return result
    
    def updateAcl(self, acl):
        """
        Updates the associated Access Control List (ACL).
        
        @param acl: Describes the ACL of the item. Every entry describes 
                    a list of granted/denied privileges of specific principal.
                    For defined privileges see L{datafinder.persistence.constants}.
        @type acl: C{dict} of C{unicode} of C{tuple} of C{list} of C{unicode}, C{list} of C{unicode}.
        """
        
        self.__privilegeStorer.updateAcl(acl)
    
    def retrievePrivileges(self):
        """
        Determines the privileges that the current user owns regarding the associated item. 
        
        @return: List of granted privileges.
                 For defined privileges see L{datafinder.persistence.constants}.
        @rtype: C{list} of C{unicode}
        """
        
        return self.__privilegeStorer.retrievePrivileges()
    
    def retrieveAcl(self):
        """
        Retrieve the ACL of the associated item.
        
        @return ACL of the item. Every entry describes 
                a list of granted/denied privileges of specific principal.
                For defined privileges see L{datafinder.persistence.constants}.
        @rtype C{dict} of C{unicode} of C{tuple} of C{list} of C{unicode}, C{list} of C{unicode}.
        """
        
        return self.__privilegeStorer.retrieveAcl()
