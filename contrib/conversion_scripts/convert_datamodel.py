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
Script to convert data models of datafinder 1.x to 2.x
"""

from gnosis.xml import objectify


__version__ = "$Revision-Id:$" 


class DataModelConverter(object):
    """ Module to convert the datamodel"""
   
    def __init__(self, oldFilePath, newFilePath):
        self._newXmlFile = open(newFilePath, "w")
              
        self._oldModel = self._importOld(oldFilePath)
        self._mapToNew()
        self._newXmlFile.close()
        
    def _importOld(self, oldFilePath):
        """ Imports the old XML data model file """
        xml_obj = objectify.XML_Objectify(oldFilePath)
        return xml_obj.make_instance() 
    
    def _mapToNew(self):
        """ 
        maps the objects from the old 
        file to the new model and writes them 
        to the new file
        """
        self._newXmlFile.write("<datamodel>\n")
        for attributes in self._oldModel.attr:
            if attributes.name == "dataTypes":
                self._mapDataTypes(attributes)
            elif attributes.name == "relationTypes":
                self._mapRelationTypes(attributes)
        self._newXmlFile.write("</datamodel>")
        
    def _mapDataTypes(self, dataTypes):
        """ 
        maps the datatype - objects from the old 
        file to the new model and writes them 
        to the new file 
        """
        for item in dataTypes.item:
            for attribute in item.attr:
                # Determine relevant properties
                if attribute.name == "name":
                    name = attribute.value
                elif attribute.name == "iconName":
                    iconName = attribute.value
                elif attribute.name == "properties":
                    try:
                        for item in attribute.item:
                            for attribute in item.attr:
                                if attribute.name == "name":
                                    propertyName = attribute.value
                                elif attribute.name == "valueType":
                                    valueType = attribute.type.capitalize()
                                elif attribute.name == "mandatory":
                                    mandatory = attribute.type.lower()
                                elif attribute.name == "defaultValue":
                                    defaultValue = attribute.value
                                properties = True
                            
                    except AttributeError:
                        print ("DataType: " + name + " has no properties defined" )
                        properties = False
                
            # Write a relation to the file
            self._newXmlFile.write("\t<datatypes>\n")
            self._newXmlFile.write("\t\t<name>" + name + "</name>\n")
            self._newXmlFile.write("\t\t<iconName>" + iconName + "</iconName>\n")
            if(properties):
                self._newXmlFile.write("\t\t<properties>\n")
                self._newXmlFile.write("\t\t\t<name>" + propertyName + "</name>\n")
                self._newXmlFile.write("\t\t\t<valueType>" + valueType + "</valueType>\n")
                self._newXmlFile.write("\t\t\t<mandatory>" + mandatory + "</mandatory>\n")
                self._newXmlFile.write("\t\t\t<defaultValue>" + defaultValue + "</defaultValue>\n")
                self._newXmlFile.write("\t\t</properties>\n")
            self._newXmlFile.write("\t</datatypes>\n")                  
    
    def _mapRelationTypes(self, relationTypes):
        """ 
        maps the relation type - objects from the old 
        file to the new model and writes them 
        to the new file
        """
        for item in relationTypes.item:
            
            # Determine relevant properties
            for attribute in item.attr:
                if attribute.name == "targetTypes":
                    targetDataTypeIds = list()
                    for item in attribute.item:
                        targetDataTypeIds.append(item.value)
                elif attribute.name == "name":
                    name = attribute.value
                elif attribute.name == "iconName":
                    iconName = attribute.value
                elif attribute.name == "sourceTypes":
                    sourceDataTypeIds = list()
                    try:
                        for item in attribute.item:
                            sourceDataTypeIds.append(item.value)
                    except AttributeError:
                        # if there is no source, root is the source and 
                        # the name of the relation must be root relation
                        name = "Root Relation"

            # Write a relation to the file
            self._newXmlFile.write("\t<relations>\n")
            self._newXmlFile.write("\t\t<name>" + name + "</name>\n")
            self._newXmlFile.write("\t\t<iconName>" + iconName + "</iconName>\n")
            for sourceDataTypeId in sourceDataTypeIds:
                self._newXmlFile.write("\t\t<sourceDataTypeNames>" + sourceDataTypeId + "</sourceDataTypeNames>\n")
            for targetDataTypeId in targetDataTypeIds:
                self._newXmlFile.write("\t\t<targetDataTypeNames>" + targetDataTypeId + "</targetDataTypeNames>\n")
            self._newXmlFile.write("\t</relations>\n")

if __name__ == "__main__":
    import sys
              
    if len(sys.argv) != 3:
        print("Usage: oldFilePath <string>, newFilePath  <string> ") # TODO: complete it
    else:
        DataModelConverter(sys.argv[1], sys.argv[2])
        print("Successfully mapped")
