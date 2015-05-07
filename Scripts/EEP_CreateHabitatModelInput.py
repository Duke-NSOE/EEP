# EEP_CreateHabitatModelInput.py
#
# Description: Adds a column to the Catchment Habitat table listing with 1's where
#   the species exists and zero where it does not.
#
# Requires: A table of species occurrences tagged by the catchments in which they
#   occur. (See Tag Occurrent Points with Catchments model).


import arcpy

# Input variables
occurrencePtsFC = arcpy.GetParameterAsText(0)
catchmentFC = arcpy.GetParameterAsText(1)

# Output variables
outputTbl = arcpy.GetParameterAsText(2)

# Script variables
tmpPts = "in_memory/tmpPts"
tmpPts2 = "in_memory/tmpPts2"

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

# ---Procedures---
# Split multipart into single parts
msg("Splitting multi-point features into single-point features")
arcpy.MultipartToSinglepart_management(occurrencePtsFC,tmpPts)

# Intersect the occurrence points and the NHD Catchments
msg("Intersecting occurrence points with NHD catchments")
arcpy.Intersect_analysis("{} #;{} # ".format(tmpPts,catchmentFC),tmpPts2,"NO_FID","","POINT")

# Add a tabulate field, set its value to 1
arcpy.AddField_management(tmpPts2,"Present","SHORT")
arcpy.CalculateField_management(tmpPts2,"Present","1")

# Pivot the records
arcpy.PivotTable_management(tmpPts2, "GRIDCODE;FEATUREID", "SCIENTIFIC", "PRESENT", outputTbl)