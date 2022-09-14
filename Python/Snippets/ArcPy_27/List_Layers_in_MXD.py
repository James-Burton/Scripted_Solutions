## list layers in current mxd:
import arcpy
mxd = arcpy.mapping.MapDocument("CURRENT")
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.supports("DATASOURCE"):
        print "Layer: " + lyr.name + "  Source: " + lyr.dataSource