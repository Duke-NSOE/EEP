# EEP_ComputeNPDES.py
#
# Description:
#   Computes the number of NPDES points within each NHD Catchment. 
#   Intersects the point feature class with the catchment catchment polygons.
#   Then summarizes the resulting table to generate a table listing the frequency 
#   of points within each catchment. 
#
# July 2015
# John.Fay@duke.edu

import sys, os, arcpy

# Input variables
catchmentFC = arcpy.GetParameterAsText(0)   # NHD Catchment polygons
npdesFC = arcpy.GetParameterAsText(1)   #

# Output variables
outputTbl = arcpy.GetParameterAsText(2)   # Ouptut table

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
msg("Intersecting points and catchments")
arcpy.Intersect_analysis("{} #;{} #".format(catchmentFC,npdesFC),xingsFC,"NO_FID","","POINT")

msg("Tabulating count of poitns in each NHD Catchment")
arcpy.Statistics_analysis(xingsFC,outputTbl,"FEATUREID COUNT","FEATUREID")

msg("Updating field names")
arcpy.AlterField_management(outputTbl,"FREQUENCY","NPDES","NPDES")
arcpy.DeleteField_management(outputTbl,"COUNT_FEATUREID")

msg("Finished")