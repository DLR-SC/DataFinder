#
# Description: The class draws a partial relation (a line) from a
#              DataTypeIcon to a RelationTypeIcon
#
# Created: Heiko Schoenert (mail to Heiko.Schoenert@dlr.de)
#
# Version: $Id: partial_relation_icon.py 3675 2009-01-08 10:38:26Z mohr_se $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
The class draws a partial relation (a line) from a
DataTypeIcon to a RelationTypeIcon
"""

 
from qt import Qt, QBrush, QColor, QPointArray
from qtcanvas import QCanvasPolygon


__version__ = "$LastChangedRevision: 3675 $"


class PartialRelationIcon(QCanvasPolygon):
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
