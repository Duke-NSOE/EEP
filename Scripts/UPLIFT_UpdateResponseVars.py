# UPLIFT_UpdateResponseVars.py
#
# Description: Updates the fields in the Response Vars FC

# Import arcpy module
import sys, os, arcpy

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

#User variables
respvarsFC = arcpy.GetParameterAsText(0) #r'c:\workspace\eep_tool\Data\EEP_030501.gdb\WU_ResponseVars'
fromJoinFld = arcpy.GetParameterAsText(1)
updateTbl = arcpy.GetParameterAsText(2)  #r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\WU_FlowlineLULC'
toJoinFld = arcpy.GetParameterAsText(3)
updateFlds = arcpy.GetParameterAsText(4) #"FLNLCD_1;FLNLCD_2"

#Set environments
arcpy.env.overwriteOutput = True

# Get paths
rootWS = os.path.dirname(sys.path[0])
dataWS = os.path.join(rootWS,"Data")

# Local variables:
rvLyr = "RespVarsLyr"

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
# Make a feature layer of the respVarsFC
msg("...creating table view of response variables")
rvLyr = arcpy.MakeTableView_management(respvarsFC,rvLyr)

# Join updateTbl to layer
msg("...joining tables")
rvJoin = arcpy.AddJoin_management(rvLyr,fromJoinFld,updateTbl,toJoinFld)

# Loop through the update fields
for fld in updateFlds.split(";"):
    msg("...updating {}".format(fld))
    
    # Get the update and calc field names
    updateFld = os.path.basename(respvarsFC) + "." + fld
    valueFld = os.path.basename(updateTbl) + "." + fld

    # Check that the update field actually exists
    if arcpy.ListFields(rvLyr,updateFld) == []:
        msg("{} field does not exist; skipping","warning")
        continue

    # Update the values
    arcpy.CalculateField_management(rvLyr,updateFld,"[{}]".format(valueFld))

#Return the merged table
arcpy.SetParameterAsText(5,respvarsFC)
