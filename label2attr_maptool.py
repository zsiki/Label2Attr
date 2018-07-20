# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Label2Attr
                                 A QGIS plugin
 Assign a label to an other layer's attribute
                              -------------------
        begin                : 2018-07-04
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Zoltan Siki
        email                : siki1958@gmail.com
 ***************************************************************************/

This tool button based on Lutra Consulting QGIS plugin NearestFeature

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.gui import QgsMapTool
from qgis.core import QgsMapToPixel, QgsFeatureRequest, QgsSpatialIndex, \
    QgsRectangle, QgsDistanceArea
from PyQt4.QtGui import QCursor, QMessageBox
from PyQt4.QtCore import Qt
import myutils

class Label2AttrMapTool(QgsMapTool):
    
    def __init__(self, canvas, plugin):
        
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
        self.plugin = plugin
        
    def activate(self):
        self.canvas.setCursor(self.cursor)
    
    def screenToLayerCoords(self, screenPos, layer):
        
        transform = self.canvas.getCoordinateTransform()
        canvasPoint = QgsMapToPixel.toMapCoordinates(transform, 
            screenPos.x(), screenPos.y())
        
        # Transform if required
        layerEPSG = layer.crs().authid()
        projectEPSG = self.canvas.mapRenderer().destinationCrs().authid()
        if layerEPSG != projectEPSG:
            renderer = self.canvas.mapRenderer()
            layerPoint = renderer.mapToLayerCoordinates(layer, canvasPoint )
        else:
            layerPoint = canvasPoint
        return layerPoint

    def canvasReleaseEvent(self, mouseEvent):
        """ 
        """
        # get nearest point in label layer
        ll = myutils.getMapLayerByName(self.plugin.labelLayer)
        # Determine the location of the click in real-world coords
        point = self.toLayerCoordinates( ll, mouseEvent.pos() )

        llIdx = QgsSpatialIndex(ll.getFeatures())
        ids = llIdx.intersects(QgsRectangle(point.x() - self.plugin.tolerance,
            point.y() - self.plugin.tolerance, point.x() + self.plugin.tolerance,
            point.y() + self.plugin.tolerance))
        if len(ids) == 0:
            QMessageBox.warning(self.plugin.iface.mainWindow(),
                self.tr("Warning"), self.tr("Point not found"))
            return
        # find nearest
        mindist = self.plugin.tolerance
        nearest = None
        d = QgsDistanceArea()
        for id in ids:
            request = QgsFeatureRequest().setFilterFid(id)
            pFeature = ll.getFeatures(request).next()
            dist = d.measureLine(pFeature.geometry().asPoint(), point)
            if dist < mindist:
                mindist = dist
                nearest = pFeature
        if nearest is None:
            QMessageBox.warning(self.plugin.iface.mainWindow(),
                self.tr("Warning"), self.tr("Point not found"))
            return
        #print nearest[self.labelColumn] 
        tl = myutils.getMapLayerByName(self.plugin.targetLayer)
        if len(tl.selectedFeatures()) != 1:
            QMessageBox.warning(self.plugin.iface.mainWindow(), self.tr("Warning"),
                self.tr("Please select a single feature in target layer"))
            return
        target = tl.selectedFeatures()[0]
        attrs = target.attributes()
        id = target.id()
        tl.startEditing()
        ind = tl.fieldNameIndex(self.plugin.targetColumn)
        #print attrs
        tl.dataProvider().changeAttributeValues({id: {ind: nearest[self.plugin.labelColumn]}})
        tl.commitChanges()
        QMessageBox.information(self.plugin.iface.mainWindow(), "Info", nearest[self.plugin.labelColumn])
        #QMessageBox.information(self.plugin.iface.mainWindow(),"Info", "X,Y = %s,%s B=%s" % (str(point.x()),str(point.y()), str(mindist)))

