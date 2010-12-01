# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#
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
The class draws a datatype icon
"""


from datafinder.gui.admin.datamodel_iconview.prototype_icon import PrototypeIcon


__version__ = "$Revision-Id:$" 


class DataTypeIcon(PrototypeIcon):
    """
    collection-icon to be shown on QCanvasView

    @param ico: the new datatype-icons image as pixmap
    @type ico: L{qt.QPixmap}

    @param ico_text: the new datatype-icons name
    @type ico_text: string

    @param canvas: the new datatype-icons canvas
    @type canvas: qt.QCanvas
    """
    def __init__(self, icnPxmp, icnLbl, icnCnvs):
        PrototypeIcon.__init__(self, icnPxmp, icnLbl, icnCnvs)

        self.iconType = 1

    def setParent(self, thisRel):
        """
        adds a relation to isParent list

        @param thisRel: the relation
        @type thisRel: qt.QCanvasPolygonalItem
        """
        self.parentOf.append(thisRel)

    def setChild(self, thisRel):
        """
        adds a relation to isChild list

        @param thisRel: the relation
        @type thisRel: qt.QCanvasPolygonalItem
        """
        self.childOf.append(thisRel)
