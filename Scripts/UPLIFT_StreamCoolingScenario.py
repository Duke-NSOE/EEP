# UPLIFT_StreamCoolingScenario.py
#
# Description: Modfies the response variables to represent a scenario of stream
#  cooling. It does so by moving percentages in each catchment classified as "warm" into
#  the "cool" category. Percentages classified as cool remains cool and those classified
#  as "cold" remain cold.
#
# The revised table is then used as an input to the ModelUplift script.

# Import arcpy module
import sys, os, arcpy

#User variables
origRVTbl = arcpy.GetParameterAsText(0)
upliftTbl = arcpy.GetParameterAsText(1)

#Set environments
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

## PROCESSES 
#Make a copy of the responseVariableTable
msg("Copying original data to ResponseVarsSC")
upliftTbl = arcpy.CopyRows_management(origRVTbl,upliftTbl)

#Increase Forest(4) flowlength to sum of Barren(3), Shrubland(5), Herbaceous(7), Cultivated(8), and Wetland(9)
msg("Moving percentages of warm stream to cool streams")
arcpy.CalculateField_management(upliftTbl,"cool","[cool]+ [warm]")

#Zero out current values
msg("Zeroing out existing warm percentages")
arcpy.CalculateField_management(upliftTbl,"warm","0")

