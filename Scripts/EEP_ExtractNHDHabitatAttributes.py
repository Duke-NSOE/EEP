# EEEP_ExtractNHDHabitatAttributes.py
#
# Extracts relevant NHD attributes for the selected NHD Catchments
#
# May 2015
# John.Fay@duke.du

import sys, os, arcpy
arcpy.env.overwriteOutput = True

# Path variables
dataPth = os.path.abspath(sys.path[0]+ "\\..\\Data")
NHDsde = os.path.join(dataPth,"NHD data.sde")

# Input variables
HUC6 = arcpy.GetParameterAsText(0)

# Output variables
OutTable = arcpy.GetParameterAsText(1)

# Program variables
NHD_Flowlines = os.path.join(NHDsde,"NHD.DBO.NHDFlowlines\NHD.DBO.NHDFlowlines")
PlusFlowlineVAA = os.path.join(NHDsde,"NHD.DBO.PlusFlowlineVAA")
Elevslope = os.path.join(NHDsde,"NHD.DBO.elevslope")
EROM_MA0001 = os.path.join(NHDsde,"NHD.DBO.NHD_EROM")
CumTotTempMA = os.path.join(NHDsde,"NHD.DBO.CumTotTempMA")
IncrTemp = os.path.join(NHDsde,"NHD.DBO.IncrTemp")
CumTotPrecipMA = os.path.join(NHDsde,"NHD.DBO.CumTotPrecipMA")
IncrPrecip = os.path.join(NHDsde,"NHD.DBO.IncrPrecip")
ROMA = os.path.join(NHDsde,"NHD.DBO.ROMA")
Incr_NLCD_2011 = os.path.join(NHDsde,"NHD.DBO.IncrNLCD2011")
Cum_Tot_NLCD_2011 = os.path.join(NHDsde,"NHD.DBO.CumTotNLCD2011")

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
                           "Q0001E;V0001E;Qincr0001E;TEMP0001;PPT0001;PET0001;QLOSS0001;Q0001E_min;Q0001_max")

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

msg("Joining Incremental NLCD_2011 ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", Incr_NLCD_2011, "FeatureID",
                           "NLCD11P;NLCD21P;NLCD22P;NLCD23P;NLCD24P;NLCD31P;NLCD41P;NLCD42P;NLCD43P;NLCD52P;NLCD71P;NLCD81P;NLCD82P;NLCD90P;NLCD95P;NLCD1;NLCD2;NLCD3;NLCD4;NLCD5;NLCD7;NLCD8;NLCD9")

msg("Joining Cumulative NLCD_2011 ({} of {})".format(x,total)); x += 1
arcpy.JoinField_management(OutTable, "COMID", Cum_Tot_NLCD_2011, "ComID",
                          "NLCD11PC;NLCD21PC;NLCD22PC;NLCD23PC;NLCD24PC;NLCD31PC;NLCD41PC;NLCD42PC;NLCD43PC;NLCD52PC;NLCD71PC;NLCD81PC;NLCD82PC;NLCD90PC;NLCD95PC;NLCD1;NLCD2;NLCD3;NLCD4;NLCD5;NLCD7;NLCD8;NLCD9")


