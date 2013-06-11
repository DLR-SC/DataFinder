# -*- coding: utf-8 -*-
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
Small integration test with a real SFTP server.
"""


__version__ = "$Revision-Id:$" 


if __name__ == "__main__":
    from datafinder.persistence.common.configuration import BaseConfiguration
    from datafinder.persistence.adapters.sftp.factory import FileSystem
    import StringIO
    bc = BaseConfiguration("sftp://192.168.64.128/home/schlauch/datafinder", username="username", password="password")
    fs = FileSystem(bc)
    
    
    root = fs.createDataStorer("/")
    
    
    fileStorer = fs.createDataStorer("/file.txt")
    print root.getChildren()
    fileStorer.writeData(StringIO.StringIO("test"))
    print fileStorer.readData().read()
    fileStorer.delete()
    print fileStorer.exists()
    
    print root.getChildren()

    recDir = fs.createDataStorer("/päth/here/there")
    recDir.createCollection(True)
    print "Collection:", recDir.exists(), recDir.isCollection, recDir.isLeaf
    
    file1 = fs.createDataStorer("/päth/file�.txt")
    file1.writeData(StringIO.StringIO("test2"))
    print file1.readData().read()
    file2 = fs.createDataStorer("/päth/file2.txt")
    file1.move(file2)
    print "file2", file2.readData().read()
    
    file2.copy(file1)
    print "file1", file1.readData().read()
    file2.copy(fs.createDataStorer("/päth/here/there/file3"))
    
    path = fs.createDataStorer("/päth")
    newPath = fs.createDataStorer("/päth2")
    path.move(newPath)
    print "path", path.exists()
    print "newPath", newPath.exists()

    newPath.copy(path)
    newPath.copy(fs.createDataStorer("/päth/here/there/12"))
    newPath.delete()
    path.delete()
    
    print root.getChildren()
