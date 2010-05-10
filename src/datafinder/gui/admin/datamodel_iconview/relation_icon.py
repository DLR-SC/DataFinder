#
# Description: This class draws a relation icon
#
# Created: Heiko Schoenert (mail to Heiko.Schoenert@dlr.de)
#
# Version: $Id: relation_icon.py 3906 2009-04-03 17:17:43Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
This class draws a relation icon.
"""


from datafinder.gui.admin.datamodel_iconview.prototype_icon import PrototypeIcon
from datafinder.gui.admin.datamodel_iconview.partial_relation_icon import PartialRelationIcon


__version__ = "$LastChangedRevision: 3906 $"


class RelationIcon(PrototypeIcon):
    """
    Relation icon to be shown on a QCanvasView.
    """

    def __init__(self, relationType, icnPxmp, icnLbl, icnCnvs):
        PrototypeIcon.__init__(self, icnPxmp, icnLbl, icnCnvs)

        self.parentOf = []
        self.childOf = []
        self.partialRelations = []
        self.relationType = relationType
        self.iconLabel = relationType.name
        self.updateLists()
        self.initPartialRelations()
        self.iconType = 2

    def initPartialRelations(self):
        """
        Creates partial relations depending on the icons RelationType form.
        """

        for eachItem in self.canvas().allItems():
            if eachItem.iconType == 1:
                if eachItem.iconLabel in self.parentOf:
                    newPartialRelation = PartialRelationIcon(self.canvas(), self, eachItem, 0)
                    self.partialRelations.append(newPartialRelation)
                    newPartialRelation.setZ(0)
                    newPartialRelation.show()
                if eachItem.iconLabel in self.childOf:
                    newPartialRelation = PartialRelationIcon(self.canvas(), self, eachItem, 1)
                    self.partialRelations.append(newPartialRelation)
                    newPartialRelation.setZ(0)
                    newPartialRelation.show()

        self.updatePartialRelations()

    def reinitialize(self):
        """
        Deletes all partial relations, updates the list of childs and parents
        and reinitializes the partial relations,
        also updates the icons label.
        """

        self.updateLists()
        iconLabel = self.relationType.name
        self.setIconLabel(iconLabel)

        for eachItem in self.partialRelations:
            eachItem.destroyIcon()
            del eachItem

        self.partialRelations = []
        self.initPartialRelations()

    def updateLists(self):
        """
        To update the relations parent and child list depending
        on data in the icons RelationType Form.
        """

        self.parentOf = self.relationType.sourceDataTypeNames
        self.childOf = self.relationType.targetDataTypeNames
