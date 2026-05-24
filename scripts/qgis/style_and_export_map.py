# qgis_scripts/style_and_export_map.py
"""
Auto-style and export map layout of watersheds, streams, and DEM base.
Run inside QGIS Python Console or via:
    qgis_process run qgis:execpython -- SCRIPT=qgis_scripts/style_and_export_map.py
"""

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsGraduatedSymbolRenderer,
    QgsRendererRange,
    QgsSymbol,
    QgsLayoutExporter,
    QgsPrintLayout,
    QgsLayoutItemMap,
    QgsLayoutItemLabel,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsUnitTypes,
)
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface
from pathlib import Path

# paths
proj_root = Path("G:/PROJECTS/watershed-up")
rasters = proj_root / "data/rasters"
watersheds_gpkg = rasters / "watersheds.gpkg"
stream_raster = rasters / "stream_network_lucknow.tif"
dem_raster = rasters / "hillshade_lucknow.tif"
export_png = rasters / "watersheds_map.png"

# Load layers
project = QgsProject.instance()

dem = QgsRasterLayer(str(dem_raster), "Hillshade")
streams = QgsRasterLayer(str(stream_raster), "Streams")
watersheds = QgsVectorLayer(f"{watersheds_gpkg}|layername=watersheds", "Watersheds", "ogr")

if not watersheds.isValid():
    raise Exception("Could not load watersheds layer")

project.addMapLayer(dem)
project.addMapLayer(streams)
project.addMapLayer(watersheds)

# Apply style: watersheds by area_km2
symbol = QgsSymbol.defaultSymbol(watersheds.geometryType())
symbol.setColor(QColor(200, 100, 100, 90))
symbol.setStrokeColor(QColor(80, 80, 80))
symbol.setStrokeWidth(0.3)

# Create graduated color ramp for area
ranges = []
minv, maxv = watersheds.minimumValue(watersheds.fields().indexOf("area_km2")), watersheds.maximumValue(watersheds.fields().indexOf("area_km2"))
steps = 5
step = (maxv - minv) / steps if steps else 1
colors = [QColor(255, 235, 205), QColor(255, 200, 160), QColor(255, 170, 120), QColor(255, 130, 80), QColor(255, 90, 40)]

for i in range(steps):
    lower = minv + i * step
    upper = lower + step
    rng_symbol = symbol.clone()
    rng_symbol.setColor(colors[i])
    ranges.append(QgsRendererRange(lower, upper, rng_symbol, f"{lower:.2f}-{upper:.2f}"))

renderer = QgsGraduatedSymbolRenderer("area_km2", ranges)
watersheds.setRenderer(renderer)
watersheds.triggerRepaint()

# Create print layout and export
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName("WatershedMapLayout")
project.layoutManager().addLayout(layout)

map_item = QgsLayoutItemMap(layout)
map_item.attemptSetSceneRect(QgsLayoutSize(250, 180, QgsUnitTypes.LayoutMillimeters))
map_item.setExtent(watersheds.extent())
layout.addLayoutItem(map_item)
map_item.attemptMove(QgsLayoutPoint(10, 10, QgsUnitTypes.LayoutMillimeters))

label = QgsLayoutItemLabel(layout)
label.setText("Watershed Delineation – Lucknow Region")
label.setFontColor(QColor(10, 10, 10))
label.setFontPointSize(14)
label.adjustSizeToText()
layout.addLayoutItem(label)
label.attemptMove(QgsLayoutPoint(10, 5, QgsUnitTypes.LayoutMillimeters))

exporter = QgsLayoutExporter(layout)
exporter.exportToImage(str(export_png), QgsLayoutExporter.ImageExportSettings())
print(f"✅ Exported map image: {export_png}")
