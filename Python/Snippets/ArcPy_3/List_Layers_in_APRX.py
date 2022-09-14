## list layers in current project map
p = arcpy.mp.ArcGISProject("CURRENT")
m = p.listMaps()[0]
for lyr in m.listLayers():
    if lyr.supports("DATASOURCE"):
       print("Layer: " + lyr.name + "  Source: " + lyr.dataSource)