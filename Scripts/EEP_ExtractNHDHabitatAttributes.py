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
NHD_Flowlines = os.path.join(NHDsde,"NHDplusV2.SDE.NHDFlowline\NHDplusV2.SDE.NHDFlowline")
PlusFlowlineVAA = os.path.join(NHDsde,"NHDplusV2.SDE.PlusFlowlineVAA")
Elevslope = os.path.join(NHDsde,"NHDplusV2.SDE.elevslope")
EROM_MA0001 = os.path.join(NHDsde,"NHDplusV2.SDE.NHD_EROM")
NHDPrecipMA = os.path.join(NHDsde,"NHDplusV2.SDE.NHDPrecipMA")
NHDRunoffMA = os.path.join(NHDsde,"NHDplusV2.SDE.NHDRunoffMA")
NHDTempMA = os.path.join(NHDsde,"NHDplusV2.SDE.NHDTempMA")
Incr_NLCD_2011 = os.path.join(NHDsde,"NHDplusV2.SDE.IncrNLCD2011")
Cum_Tot_NLCD_2011 = os.path.join(NHDsde,"NHDplusV2.SDE.CumTotNLCD2011")


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

msg("Joining Flowline VAA (1 of 8)")
msg("-->Stream order,Path length, Arbolate sum, Area (sq km), Total drainage area (sq km)")
arcpy.JoinField_management(OutTable, "COMID", PlusFlowlineVAA, "ComID", "StreamOrde;Pathlength;ArbolateSu;AreaSqKM;TotDASqKM")

msg("Joining Elevslope (2 of 8)")
msg("-->Slope")
arcpy.JoinField_management(OutTable, "COMID", Elevslope, "COMID", "SLOPE")

msg("Joining EROM_MA001 (3 of 8)")
msg("-->...")
arcpy.JoinField_management(OutTable, "COMID", EROM_MA0001, "Comid", "Q0001E;V0001E;Qincr0001E;TEMP0001;PPT0001;PET0001;QLOSS0001;Q0001E_01;Q0001E_02;Q0001E_03;Q0001E_04;Q0001E_05;Q0001E_06;Q0001E_07;Q0001E_08;Q0001E_09;Q0001E_10;Q0001E_11;Q0001E_12")

msg("Joining NHDTempMA (4 of 8)")
arcpy.JoinField_management(OutTable, "COMID", NHDTempMA, "FeatureID", "TempV")

msg("Joining NHDPrecipMA (5 of 8)")
arcpy.JoinField_management(OutTable, "COMID", NHDPrecipMA, "FeatureID", "PrecipV")

msg("Joining Mean Annual Runoff (6 of 8)")
arcpy.JoinField_management(OutTable, "COMID", NHDRunoffMA, "FeatureID", "RunOffV;MinMonthly")

msg("Joining Incremental NLCD_2011 (7 of 8)")
arcpy.JoinField_management(OutTable, "COMID", Incr_NLCD_2011, "FeatureID", "NLCD11P;NLCD12P;NLCD21P;NLCD22P;NLCD23P;NLCD24P;NLCD31P;NLCD41P;NLCD42P;NLCD43P;NLCD51P;NLCD52P;NLCD71P;NLCD72P;NLCD73P;NLCD74P;NLCD81P;NLCD82P;NLCD90P;NLCD95P")

msg("Joining Cumulative Tot NLCD_2011 (8 of 8)")
arcpy.JoinField_management(OutTable, "COMID", Cum_Tot_NLCD_2011, "ComID", "NLCD11PC;NLCD12PC;NLCD21PC;NLCD22PC;NLCD23PC;NLCD24PC;NLCD31PC;NLCD41PC;NLCD42PC;NLCD43PC;NLCD51PC;NLCD52PC;NLCD71PC;NLCD72PC;NLCD73PC;NLCD74PC;NLCD81PC;NLCD82PC;NLCD90PC;NLCD95PC")

