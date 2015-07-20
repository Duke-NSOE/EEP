# EEP_ComputeFlowlineShadeStats.py
#
# Description:
#   Computes the number of road crossings within each NHD Catchment. Intersects
#   the supplied roads polyline feature class with the streams feature class,
#   and catchment polygons. Then summarizes the resulting table to
#   generate a table listing the frequency of intersections within each catchment. 
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy

# Input variables
catchmentFC = arcpy.GetParameterAsText(0)   # NHD Catchment polygons
flowlineFC = arcpy.GetParameterAsText(1)    # NHD Flowlines
roadsFC = arcpy.GetParameterAsText(2)       # NC DOT (or other) road features

# Output variables
roadXingTbl = arcpy.GetParameterAsText(3)   # Ouptut table

# Script variables
xingsFC = "in_memory/Xings"

# Environment variables
arcpy.env.overwriteOutput = True

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
msg("Intersecting roads and flowlines")
arcpy.Intersect_analysis("{} #;{} #".format(flowlineFC,roadsFC),xingsFC,"NO_FID","","POINT")

msg("Tabulating count of crossings for each NHD Catchment")
arcpy.Statistics_analysis(xingsFC,roadXingTbl,"FEATUREID FEATUREID","COMID")

msg("Updating field names")
arcpy.AlterField_management(roadXingTbl,"FREQUENCY","Crossings","Road Crossings")
arcpy.DeleteField_management(roadXingTbl,"COUNT_FEATUREID")

msg("Finished")