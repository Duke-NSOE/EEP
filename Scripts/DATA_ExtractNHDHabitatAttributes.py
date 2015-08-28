# DATA_ExtractNHDHabitatAttributes.py
#
# Extracts relevant NHD attributes for the selected NHD Catchments
#
# Aug 2015
# John.Fay@duke.du

import sys, os, arcpy
arcpy.env.overwriteOutput = True

# Path variables
dataPth = os.path.abspath(sys.path[0]+ "\\..\\Data")
NHDgdb = os.path.join(dataPth,"NHD.gdb")

# Input variables
HUC6 = arcpy.GetParameterAsText(0)

# Output variables
OutTable = arcpy.GetParameterAsText(1)

# Program variables
NHD_Flowlines = os.path.join(NHDgdb,"NHDFlowlines\NHDFlowlines")
PlusFlowlineVAA = os.path.join(NHDgdb,"PlusFlowlineVAA")
Elevslope = os.path.join(NHDgdb,"elevslope")
EROM_MA0001 = os.path.join(NHDgdb,"NHD_EROM")
CumTotTempMA = os.path.join(NHDgdb,"CumTotTempMA")
IncrTemp = os.path.join(NHDgdb,"IncrTemp")
CumTotPrecipMA = os.path.join(NHDgdb,"CumTotPrecipMA")
IncrPrecip = os.path.join(NHDgdb,"IncrPrecip")
ROMA = os.path.join(NHDgdb,"ROMA")
Incr_NLCD_2011 = os.path.join(NHDgdb,"IncrNLCD2011")
Cum_Tot_NLCD_2011 = os.path.join(NHDgdb,"CumTotNLCD2011")

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
msg("Extracting flowline records for HUC {}".format(HUC6))
arcpy.TableSelect_analysis(NHD_Flowlines, OutTable, "REACHCODE LIKE '{}%'".format(HUC6))

# Get the count of selected records
count = arcpy.GetCount_management(OutTable).getOutput(0)
msg("{} records extracted".format(count))

msg("Dropping fields")
keepFields = ("OBJECTID","COMID","LENGTHKM","REACHCODE","WBARACOMI","FTYPE","FCODE")
for fld in arcpy.ListFields(OutTable):
    if not (fld.name in keepFields):
        arcpy.DeleteField_management(OutTable,[fld.name])

# Add attribute index
msg("Adding an attribute index to speed processing")
arcpy.AddIndex_management(OutTable,"COMID","COMID","UNIQUE","NON_ASCENDING")

# Status counter
x = 1; total = 10

# Join tables (send message/increase counter; join fields)
## PlusFlowlineVAA
msg("Joining Flowline VAA ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", PlusFlowlineVAA, "ComID", "StreamOrde;Pathlength;ArbolateSu;TotDASqKM")

## elevslope
msg("Joining Elevslope ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", Elevslope, "COMID", "SLOPE")

## EROM_MA0001
msg("Joining EROM_MA0001 ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", EROM_MA0001, "Comid",
                           "Q0001E;V0001E;Qincr0001E;TEMP0001;PPT0001;PET0001;QLOSS0001;Q0001E_min;Q0001E_max")

## CumTemp
msg("Joining CumTotTempMA ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", CumTotTempMA, "ComID", "TempVC")

## IncrTemp
msg("Joining IncrTemp ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", IncrTemp, "FeatureID","TempVMA;Temp_min;Temp_max")

## CumPrecip
msg("Joining CumTotPrecipMA ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", CumTotPrecipMA, "ComID", "PrecipVC")

## IncrPrecip
msg("Joining IncrPrecip ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", IncrPrecip,"FeatureID","PrecipVMA;Precip_min;Precip_max")

## ROMA (Runoff)
msg("Joining Runoff data (ROMA) ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", ROMA, "FeatureID","RunOffVMA;RunOff_min;RunOff_max")

## Incremental NLCD
msg("Joining Incremental NLCD_2011 ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", Incr_NLCD_2011, "FeatureID","NLCD1;NLCD2;NLCD3;NLCD4;NLCD5;NLCD7;NLCD8;NLCD9")

## Cumulative NLCD
msg("Joining Cumulative NLCD_2011 ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", Cum_Tot_NLCD_2011, "ComID","NLCD1c;NLCD2c;NLCD3c;NLCD4c;NLCD5c;NLCD7c;NLCD8c;NLCD9c")

msg("Finished!")
