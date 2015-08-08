# UPLIFT_RiparianBufferScenario.py
#
# Description: Copies the master response variable table and modifies values
#  so that all FlowLineNLCD values that arent' water/developed/forest become
#  forest. This involved setting FLNLCD_X (X=3,5,7,8) to zero and taking the
#  sum of their original values and adding them to existing values. 
#
# The revised table is then used as an input to the ModelUplift script.

# Import arcpy module
import sys, os, arcpy

#User variables
origRVTbl = r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\ResponseVars'
upliftTbl = r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\ResponseVars_BU'

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
msg("Copying original data to ResponseVarsBU")
upliftTbl = arcpy.CopyRows_management(origRVTbl,upliftTbl)

#Increase Forest(4) flowlength to sum of Barren(3), Shrubland(5), Herbaceious(7), Cultivated(8), and Wetland(9)
msg("Adding lengths in Barren(3), Shrubland(5), Herbaceious(7), Cultivated(8), and Wetland(9) to existing Forest(4)")
arcpy.CalculateField_management(upliftTbl,"FLNLCD_4","[FLNLCD_4] + [FLNLCD_3] + [FLNLCD_5] + [FLNLCD_7] + [FLNLCD_8]+ [FLNLCD_9]")

#Zero out current values
msg("Zeroing out existing lenths in Barren(3), Shrubland(5), Herbaceious(7), Cultivated(8), and Wetland(9)")
arcpy.CalculateField_management(upliftTbl,"FLNLCD_3","0")
arcpy.CalculateField_management(upliftTbl,"FLNLCD_5","0")
arcpy.CalculateField_management(upliftTbl,"FLNLCD_7","0")
arcpy.CalculateField_management(upliftTbl,"FLNLCD_8","0")
arcpy.CalculateField_management(upliftTbl,"FLNLCD_9","0")

