# EEP_ComputeFlowlineTemperature.py
#
# Description: Creates a table listing the lengths of stream classified as
#  cool, moderate, warm within each catchment.
#
# Requires: The NC Stream temperature feature class, located in the
#   NC.SDE file (found in the Data folder) 
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy
arcpy.CheckOutExtension("spatial")

# Input variables
catchmentsFC = arcpy.GetParameterAsText(0)
thermalFC = arcpy.GetParameterAsText(1)

# Output variables
flowlineTemperatureTbl = arcpy.GetParameterAsText(2)

# Script variables
thermalFC_1 = "in_memory/StreamTemp"
thermalStats = "in_memory/ThermalStats"
thermalStatsPivot = "in_memory/ThermalStatsPivot"

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
## Select stream features within catchments
msg("Subsetting stream features")
thermalLyr  = arcpy.MakeFeatureLayer_management(thermalFC,"thermalLyr")
arcpy.SelectLayerByLocation_management(thermalLyr,"HAVE_THEIR_CENTER_IN",catchmentsFC)

## Tag each stream habitat feature with the NHD Feature ID
msg("Tagging thermal stream features with catchment IDs")
arcpy.Intersect_analysis("{} #;{} # ".format(thermalLyr,catchmentsFC), thermalFC_1,"NO_FID","","LINE")

## Summarize stats for each thermal class (labeled as the "HABITAT" field
msg("Tabuluating stream temperature statistics for each catchment")
arcpy.Statistics_analysis(thermalFC_1,thermalStats,[["LENGTH", "SUM"]],["HABITAT", "FEATUREID"])
arcpy.Delete_management(thermalFC_1)

##Pivot the table to create a column for each temperature [HABITAT] class
msg("Cross tabulating statistics")
arcpy.PivotTable_management(thermalStats,"FEATUREID", "HABITAT", "SUM_LENGTH", flowlineTemperatureTbl)
arcpy.Delete_management(thermalStats)

##Need to add fields, if they don't exist (i.e. if no streams of that type exist in the HUC6
#make a list of fields
flds = []
for f in arcpy.ListFields(flowlineTemperatureTbl):
    flds.append(f.name)
#add the field if it doesn't exist
if not "cold" in (flds):
    arcpy.AddField_management(flowlineTemperatureTbl,"cold","DOUBLE")
    arcpy.CalculateField_management(flowlineTemperatureTbl,"cold",0)
if not "cool" in (flds):
    arcpy.AddField_management(flowlineTemperatureTbl,"cool","DOUBLE")
    arcpy.CalculateField_management(flowlineTemperatureTbl,"cool",0)
if not "warm" in (flds):
    arcpy.AddField_management(flowlineTemperatureTbl,"warm","DOUBLE")
    arcpy.CalculateField_management(flowlineTemperatureTbl,"warm",0)

##Add total length field to table and calculate percentages
msg("Converting percentages to absolute values")
arcpy.AddField_management(flowlineTemperatureTbl,"TotLength", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(flowlineTemperatureTbl,"TotLength", "[cold]+ [cool]+ [warm]", "VB", "")
arcpy.CalculateField_management(flowlineTemperatureTbl,"cold", "[cold] / [TotLength] * 100.0", "VB", "")
arcpy.CalculateField_management(flowlineTemperatureTbl,"cool", "[cool] / [TotLength] * 100.0", "VB", "")
arcpy.CalculateField_management(flowlineTemperatureTbl,"warm", "[warm] / [TotLength] * 100.0", "VB", "")

msg("Finished!") 
