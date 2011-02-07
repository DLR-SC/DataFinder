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
script to convert datamodels of datafinder 1.x to 2.x
"""


__version__ = "$Revision-Id:$" 

from gnosis import xml
from gnosis.xml import objectify
class dataModelConvert:
    def __init__(self, oldfile, newfile):
        self.oldXmlFile = oldfile
        self.newXmlFile = open(newfile, 'w')
        
              
        self.py_obj = self.importOld()
        self.maptoNew()
        
    def importOld(self):
        xml_obj = xml.objectify.XML_Objectify(self.oldXmlFile)
        self.py_obj = xml_obj.make_instance() 
        return self.py_obj
    def mapDataTypes(self, dataTypeObject):
        for item in dataTypeObject.item:
            self.newXmlFile.write("\t<datatypes>\n")
            for attribute in item.attr: # kein pyobj mehr?.. .no id, new way of walking through??
                if attribute.name =="name":
                    name = attribute.value
                elif attribute.name =="iconName":
                    iconName = attribute.value
                elif attribute.name =="properties":
                    self.newXmlFile.write("\t\t<name>"+name+"</name>\n")
                    self.newXmlFile.write("\t\t<iconName>"+iconName+"</iconName>\n")
                    try:
                        for item in attribute.item:
                            for attribute in item.attr:
                                if attribute.name == "name":
                                    propertyname = attribute.value
                                elif attribute.name == "valueType":
                                    valueType = attribute.type
                                elif attribute.name == "mandatory":
                                    mandatory = attribute.type
                                elif attribute.name == "defaultValue":
                                    defaultValue = attribute.value
                            self.newXmlFile.write("\t\t<properties>\n")
                            self.newXmlFile.write("\t\t\t<name>"+propertyname+"</name>\n")
                            self.newXmlFile.write("\t\t\t<valueType>"+valueType+"</valueType>\n")
                            self.newXmlFile.write("\t\t\t<mandatory>"+mandatory+"</mandatory>\n")
                            self.newXmlFile.write("\t\t\t<defaultValue>"+defaultValue+"</defaultValue>\n")
                            self.newXmlFile.write("\t\t</properties>\n")
                    except AttributeError:
                        pass
            self.newXmlFile.write("\t</datatypes>\n")                  
    
    def maptoNew(self):
        self.newXmlFile.write("<datamodel>\n")
        for attributes in self.py_obj.attr:
            if attributes.name =="dataTypes":
                self.mapDataTypes(attributes)
            elif attributes.name =="relationTypes":
                self.mapRelationTypes(attributes)
        self.newXmlFile.write("</datamodel>")
    
    def writeToNew(self):
        pass
    
    def saveasNew(self):
        pass
    
    def mapRelationTypes(self, relationTypesObject):
        for item in relationTypesObject.item:
            
            for attribute in item.attr:
                if attribute.name == "targetTypes":
                    targetList = []
                    for item in attribute.item:
                        targetList.append(item.value)

                elif attribute.name =="name":
                    name = attribute.value
                elif attribute.name =="iconName":
                    iconName = attribute.value

                elif attribute.name == "sourceTypes":
                    sourceList = []
                    try:
                        for item in attribute.item:
                            sourceList.append(item.value)
                            
                    except AttributeError:
                        pass
            self.newXmlFile.write("\t<relation>\n")
            self.newXmlFile.write("\t\t<name>"+name+"</name>\n")
            self.newXmlFile.write("\t\t<iconName>"+iconName+"</iconName>\n")
            for element in sourceList:
                self.newXmlFile.write("\t\t<sourceDataTypeNames>"+element+"</sourceDataTypeNames>\n")
            for element in targetList:
                self.newXmlFile.write("\t\t<targetDataTypeNames>"+element+"</targetDataTypeNames>\n")

            self.newXmlFile.write("\t</relation>\n")
                            
old = "testfiles/trace_datamodel_old.xml"
new = "testfiles/trace_datamodel_new.xml"

conversion = dataModelConvert(old,new)
print "mapped"

