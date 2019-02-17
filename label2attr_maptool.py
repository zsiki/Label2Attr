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
    QgsRectangle, QgsDistanceArea, QgsProject, QgsFeature

from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

class Label2AttrMapTool(QgsMapTool):
    """ class for tool button """
    def __init__(self, plugin):

        super(Label2AttrMapTool, self).__init__(plugin.canvas)
        #self.canvas = plugin.canvas
        self.cursor = QCursor(Qt.CrossCursor)
        self.plugin = plugin

    def activate(self):
        """ set tool cursor """
        self.plugin.canvas.setCursor(self.cursor)

    def screenToLayerCoords(self, screenPos, layer):
        """ convert click position to CRS """
        transform = self.plugin.canvas.getCoordinateTransform()
        canvasPoint = QgsMapToPixel.toMapCoordinates(transform,
            screenPos.x(), screenPos.y())

        # Transform if required
        layerEPSG = layer.crs().authid()
        projectEPSG = self.plugin.canvas.mapRenderer().destinationCrs().authid()
        if layerEPSG != projectEPSG:
            renderer = self.plugin.canvas.mapRenderer()
            layerPoint = renderer.mapToLayerCoordinates(layer, canvasPoint)
        else:
            layerPoint = canvasPoint
        return layerPoint

    def canvasReleaseEvent(self, mouseEvent):
        """ process click position """
        # get nearest point in label layer
        ll = QgsProject.instance().mapLayersByName(self.plugin.labelLayer)[0]
        # Determine the location of the click in real-world coords
        point = self.toLayerCoordinates(ll, mouseEvent.pos())
        # find features in tolerance
        llIdx = QgsSpatialIndex(ll.getFeatures())
        ids = llIdx.intersects(QgsRectangle(
            point.x() - self.plugin.tolerance,
            point.y() - self.plugin.tolerance,
            point.x() + self.plugin.tolerance,
            point.y() + self.plugin.tolerance))
        if not ids:
            QMessageBox.warning(self.plugin.iface.mainWindow(),
                self.tr("Warning"), self.tr("Point not found"))
            return
        # find nearest
        pFeature = QgsFeature()
        mindist = self.plugin.tolerance
        nearest = None
        d = QgsDistanceArea()
        for my_id in ids:
            request = QgsFeatureRequest().setFilterFid(my_id)
            if ll.getFeatures(request).nextFeature(pFeature):
                dist = d.measureLine(pFeature.geometry().asPoint(), point)
                if dist < mindist:
                    mindist = dist
                    nearest = pFeature
        if nearest is None:
            QMessageBox.warning(self.plugin.iface.mainWindow(),
                self.tr("Warning"), self.tr("Point not found"))
            return
        tl = QgsProject.instance().mapLayersByName(self.plugin.targetLayer)[0]
        if len(tl.selectedFeatures()) != 1:
            QMessageBox.warning(self.plugin.iface.mainWindow(), self.tr("Warning"),
                self.tr("Please select a single feature in target layer"))
            return
        # update target attribute
        target = tl.selectedFeatures()[0]
        fid = target.id()
        tl.startEditing()
        ind = tl.fields().indexFromName(self.plugin.targetColumn)
        #tl.dataProvider().changeAttributeValues({fid: {ind: nearest[self.plugin.labelColumn]}}) #this does not update open data table
        tl.changeAttributeValue(fid, ind, nearest[self.plugin.labelColumn])
        tl.commitChanges()
        QMessageBox.information(self.plugin.iface.mainWindow(), "Info", str(nearest[self.plugin.labelColumn]))
