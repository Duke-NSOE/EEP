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
## Tag each stream habitat feature with the NHD Feature ID
msg("Tagging thermal stream features with catchment IDs")
#arcpy.Identity_analysis(thermalFC,catchmentsFC,termalFC_1,"NO_FID", "#", "NO_RELATIONSHIPS")
arcpy.Intersect_analysis("{} #;{} # ".format(thermalFC,catchmentsFC), thermalFC_1,"NO_FID","","LINE")
## Select 

## Summarize stats for each thermal class
msg("Tabuluating stream temperature statistics for each catchment")
arcpy.Statistics_analysis(thermalFC_1,thermalStats,[["LENGTH", "SUM"]],["HABITAT", "FEATUREID"])
arcpy.Delete_management(thermalFC_1)

##Pivot the table to create a column for each temperature [HABITAT] class
msg("Cross tabulating statistics")
arcpy.PivotTable_management(thermalStats,"FEATUREID", "HABITAT", "SUM_LENGTH", flowlineTemperatureTbl)
arcpy.Delete_management(thermalStats)

##Add total length field to table and calculate percentages
msg("Converting percentages to absolute values")
arcpy.AddField_management(flowlineTemperatureTbl,"TotLength", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(flowlineTemperatureTbl,"TotLength", "[cold]+ [cool]+ [warm]", "VB", "")
arcpy.CalculateField_management(flowlineTemperatureTbl,"cold", "[cold] / [TotLength] * 100.0", "VB", "")
arcpy.CalculateField_management(flowlineTemperatureTbl,"cool", "[cool] / [TotLength] * 100.0", "VB", "")
arcpy.CalculateField_management(flowlineTemperatureTbl,"warm", "[warm] / [TotLength] * 100.0", "VB", "")

msg("Finished!") 
