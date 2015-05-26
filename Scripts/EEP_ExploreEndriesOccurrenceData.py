# EEP_ExploreEndriesOccurrenceData.py
#
# Description: Splits the observation records in ENDRIES occurrence points
#  occurring in the selected HUC6 into single points (1 feature per occurrence)
#  and tags each point with the HUC8 in which it was found. Then summarizes
#  the data into a list of how many HUC 6s and HUC6s the species was observed. 
#  This enables the user to identify which species have a good number of records 
#  in the HUC6

import arcpy

# Input variables
occurrencePtsFC = arcpy.GetParameterAsText(0)
HUC12FC = arcpy.GetParameterAsText(1)

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
arcpy.Intersect_analysis("{} #;{} # ".format(tmpPts,HUC12FC),tmpPts2,"NO_FID","","POINT")

# Summaries the data
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "AquaticSpeciesOccurrences_Ex2"
arcpy.Frequency_analysis(tmpPts2,outputTbl,["CommonName","Scientific","HUC_8"])
