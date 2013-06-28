# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#Redistribution and use in source and binary forms, with or without
# All rights reserved.
#modification, are permitted provided that the following conditions are
#
#met:
#
#
# * Redistributions of source code must retain the above copyright 
#
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
The class draws a partial relation (a line) from a
DataTypeIcon to a RelationTypeIcon
"""

 
from qt import Qt, QBrush, QColor, QPointArray
from qtcanvas import QCanvasPolygon


__version__ = "$Revision-Id:$" 


class PartialRelationIcon(QCanvasPolygon):
    """ Represents a partial relation. """
    
    def __init__(self, relCnvs, relIcn, colIcn, relType):
        """
        initiates the partial relation and sets the connected
        relation and collection icon
        """
        QCanvasPolygon.__init__(self, relCnvs)
        
        self.relationIcon   = relIcn
        self.collectionIcon = colIcn
        self.relationType   = relType
        self.iconLabel      = ""
        self.iconType       = 3
        self.lineWidth      = 1
        
        self.relPoints      = QPointArray(8)
        self.collectionIcon.partialRelations.append(self)
    
        self.unmark()

    def mark(self):
        """
        to highlight the partial relation and connection relation
        and collection (if they're not marked yet)
        """
        if self.relationType == 0:
            self.setBrush(QBrush(QColor(0, 0, 255), Qt.SolidPattern))
        else:
            self.setBrush(QBrush(QColor(0, 180, 0), Qt.SolidPattern))

        self.setZ(200)
        self.lineWidth = 2


        if self.relationIcon.isMarked != 1:
            self.relationIcon.mark(False)
        if self.collectionIcon.isMarked != 1:
            self.collectionIcon.mark(False)
          
        self.setCoords()

    def unmark(self):
        """
        to turn off the highlight of this partial relation and the
        connected collection and relation icon
        """
        self.setZ(0)
        self.lineWidth = 1

        if self.relationType == 0:
            self.setBrush(QBrush(QColor(200, 200, 255), Qt.SolidPattern))
        else:
            self.setBrush(QBrush(QColor(200, 255, 200), Qt.SolidPattern))
        self.relationIcon.unmark(False)
        self.collectionIcon.unmark(False)

        self.setCoords()

    def getIconType(self):
        """
        return iconType
        """
        return self.iconType
    
    def setCoords(self):
        """
        to set the coordinates of the drawn polygon depending
        on the position of connected relation and collection icon
        """
        relAnchorPoint = self.relationIcon.getAnchorPoint()
        colAnchorPoint = self.collectionIcon.getAnchorPoint()

        self.relPoints.setPoint(0, relAnchorPoint)

        if self.relationType == 0:
            self.relPoints.setPoint(1, relAnchorPoint.x(),
                                     (relAnchorPoint.y() + colAnchorPoint.y()) / 2)
            self.relPoints.setPoint(2, colAnchorPoint.x(),
                                     (relAnchorPoint.y() + colAnchorPoint.y()) / 2)

        else:
            self.relPoints.setPoint(1, (relAnchorPoint.x() + colAnchorPoint.x()) / 2,
                                     relAnchorPoint.y())
            self.relPoints.setPoint(2, (relAnchorPoint.x() + colAnchorPoint.x()) / 2,
                                     colAnchorPoint.y())

        self.relPoints.setPoint(3, self.collectionIcon.getAnchorPoint())
        self.relPoints.setPoint(4, self.relPoints.point(3)[0] - self.lineWidth, self.relPoints.point(3)[1] - self.lineWidth)
        self.relPoints.setPoint(5, self.relPoints.point(2)[0] - self.lineWidth, self.relPoints.point(2)[1] - self.lineWidth)
        self.relPoints.setPoint(6, self.relPoints.point(1)[0] - self.lineWidth, self.relPoints.point(1)[1] - self.lineWidth)
        self.relPoints.setPoint(7, self.relPoints.point(0)[0] - self.lineWidth, self.relPoints.point(0)[1] - self.lineWidth)
        self.setPoints(self.relPoints)
        
    def destroyIcon(self):
        """
        completely removes the partial relation from the canvas
        """
        self.collectionIcon.removePartialRelation(self)
        self.setCanvas(None)
