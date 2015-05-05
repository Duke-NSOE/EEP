# EEP_ComputeFlowlineShadeStats.py
#
# Description:
#   Extracts stream segments within each NHD catchment falling beneath forest areas (NLCD 2011).
#   Does so by extracting forested pixels from the NLCD 2011 dataset and converting them to
#   polygons. Then tags each NHD flowline with 
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy
from arcpy import sa
arcpy.CheckOutExtension("spatial")

# Input variables
flowlineFC = arcpy.GetParameterAsText(0)
nlcdRaster = arcpy.GetParameterAsText(1)

# Output variables
shadestatsTbl = arcpy.GetParameterAsText(2)

# Script variables
forestPoly = "in_memory/ForestPolys"
shadeFlow = "in_memory/ShadeFlow"
shadeFlow2 = "in_memory/ShadeFlow2"
shadeStats = "in_memory/ShadeStats"

# Environment variables
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = nlcdRaster
arcpy.env.cellSize = nlcdRaster

# ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)


# ---Processes---
msg("Extracting forest pixels from NLCD")
forestRaster = sa.Con(nlcdRaster,1,0,"VALUE IN (41, 42, 43)")

msg("Converting to polygon")
arcpy.RasterToPolygon_conversion(forestRaster,forestPoly,"NO_SIMPLIFY","VALUE")

msg("Tagging flowline segments with forest/not forest ID (via Identify tool)")
arcpy.Identity_analysis(flowlineFC,forestPoly,shadeFlow, "ALL", "#", "NO_RELATIONSHIPS")
arcpy.Delete_management(forestPoly)

msg("Dissolving on COMID and Forest/Non-Forest")
arcpy.Dissolve_management(shadeFlow,shadeFlow2,["COMID","GRIDCODE"],"#","SINGLE_PART","DISSOLVE_LINES")
arcpy.Delete_management(shadeFlow)

msg("Updating feature lengths")
arcpy.AddGeometryAttributes_management(shadeFlow2,"LENGTH","METERS")

msg("Crosstabulating forest/non-forest lengths by catchment")
arcpy.PivotTable_management(shadeFlow2, "COMID", "gridcode", "LENGTH", shadeStats)
arcpy.Delete_management(shadeFlow2)

msg("Calculating summary statistics")
arcpy.Statistics_analysis(shadeStats,shadestatsTbl,"gridcode1 SUM; gridcode1 MAX; gridcode1 MEAN", "COMID")
arcpy.Delete_management(shadeStats)

msg("Updating field names")
arcpy.AlterField_management(shadestatsTbl,"FREQUENCY","ShadedSegments","ShadedSegments")
arcpy.AlterField_management(shadestatsTbl,"SUM_gridcode1","ShadedLength","ShadedLength")
arcpy.AlterField_management(shadestatsTbl,"MEAN_gridcode1","MeanShadeLength","MeanShadeLength")
arcpy.AlterField_management(shadestatsTbl,"MAX_gridcode1","LongestSegment","LongestSegment")

msg("Finished!")
