# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# tmp.py
# Created on: 2015-05-06 15:44:34.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: tmp <HUC_6> <HUC_GDB> <HabitatTable__10_> 
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy

# Script arguments
HUC_6 = arcpy.GetParameterAsText(0)
if HUC_6 == '#' or not HUC_6:
    HUC_6 = "06010202" # provide a default value if unspecified

HUC_GDB = arcpy.GetParameterAsText(1)

HabitatTable__10_ = arcpy.GetParameterAsText(2)
if HabitatTable__10_ == '#' or not HabitatTable__10_:
    HabitatTable__10_ = "C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\EEP_%HUC 6%.gdb\\HabitatTable" # provide a default value if unspecified

# Local variables:
HabitatTable = HUC_6
HabitatTable__2_ = HabitatTable
HabitatTable__3_ = HabitatTable__2_
HabitatTable__4_ = HabitatTable__3_
HabitatTable__5_ = HabitatTable__4_
HabitatTable__6_ = HabitatTable__5_
HabitatTable__7_ = HabitatTable__6_
HabitatTable__8_ = HabitatTable__7_
HabitatTable__9_ = HabitatTable__8_
Row_Count = HabitatTable
NHD_Flowlines = "C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.NHDFlowline\\NHDplusV2.SDE.NHDFlowline"
PlusFlowlineVAA = "C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.PlusFlowlineVAA"
Elevslope = "C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.elevslope"
EROM_MA0001 = "C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.NHD_EROM"
Incr_NLCD2_011 = "C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.IncrNLCD2011"
NHDPrecipMA = "C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.NHDPrecipMA"
NHDRunoffMA = "C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.NHDRunoffMA"
NHDTempMA = "C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.NHDTempMA"
Cum_Tot_NLCD_2011 = "C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.CumTotNLCD2011"

# Process: Table to Table
arcpy.TableToTable_conversion(NHD_Flowlines, HUC_GDB, "HabitatTable", "REACHCODE LIKE '%HUC 6%%'", "COMID \"COMID\" true true false 4 Long 0 10 ,First,#,C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.NHDFlowline\\NHDplusV2.SDE.NHDFlowline,COMID,-1,-1;LENGTHKM \"LENGTHKM\" true true false 8 Double 11 18 ,First,#,C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.NHDFlowline\\NHDplusV2.SDE.NHDFlowline,LENGTHKM,-1,-1;REACHCODE \"REACHCODE\" true true false 14 Text 0 0 ,First,#,C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.NHDFlowline\\NHDplusV2.SDE.NHDFlowline,REACHCODE,-1,-1;WBAREACOMI \"WBAREACOMI\" true true false 4 Long 0 10 ,First,#,C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.NHDFlowline\\NHDplusV2.SDE.NHDFlowline,WBAREACOMI,-1,-1;FTYPE \"FTYPE\" true true false 24 Text 0 0 ,First,#,C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.NHDFlowline\\NHDplusV2.SDE.NHDFlowline,FTYPE,-1,-1;FCODE \"FCODE\" true true false 4 Long 0 10 ,First,#,C:\\WorkSpace\\EEP_Spring2015\\EEP_Tool\\Data\\NHD data.sde\\NHDplusV2.SDE.NHDFlowline\\NHDplusV2.SDE.NHDFlowline,FCODE,-1,-1", "")

# Process: Get Count
arcpy.GetCount_management(HabitatTable)

# Process: Add Attribute Index
arcpy.AddIndex_management(HabitatTable, "COMID", "COMID", "UNIQUE", "NON_ASCENDING")

# Process: Join Field
arcpy.JoinField_management(HabitatTable__2_, "COMID", PlusFlowlineVAA, "ComID", "StreamOrde;Pathlength;ArbolateSu;AreaSqKM;TotDASqKM")

# Process: Join Field (2)
arcpy.JoinField_management(HabitatTable__3_, "COMID", Elevslope, "COMID", "SLOPE")

# Process: Join Field (3)
arcpy.JoinField_management(HabitatTable__4_, "COMID", EROM_MA0001, "Comid", "Q0001E;V0001E;Qincr0001E;TEMP0001;PPT0001;PET0001;QLOSS0001;Q0001E_01;Q0001E_02;Q0001E_03;Q0001E_04;Q0001E_05;Q0001E_06;Q0001E_07;Q0001E_08;Q0001E_09;Q0001E_10;Q0001E_11;Q0001E_12")

# Process: Join Field (4)
arcpy.JoinField_management(HabitatTable__5_, "COMID", NHDTempMA, "FeatureID", "TempV")

# Process: Join Field (5)
arcpy.JoinField_management(HabitatTable__6_, "COMID", NHDPrecipMA, "FeatureID", "PrecipV")

# Process: Join Field (6)
arcpy.JoinField_management(HabitatTable__7_, "COMID", NHDRunoffMA, "FeatureID", "RunOffV;MinMonthly")

# Process: Join Field (7)
arcpy.JoinField_management(HabitatTable__8_, "COMID", Incr_NLCD2_011, "FeatureID", "NLCD11P;NLCD12P;NLCD21P;NLCD22P;NLCD23P;NLCD24P;NLCD31P;NLCD41P;NLCD42P;NLCD43P;NLCD51P;NLCD52P;NLCD71P;NLCD72P;NLCD73P;NLCD74P;NLCD81P;NLCD82P;NLCD90P;NLCD95P")

# Process: Join Field (8)
arcpy.JoinField_management(HabitatTable__9_, "COMID", Cum_Tot_NLCD_2011, "ComID", "NLCD11PC;NLCD12PC;NLCD21PC;NLCD22PC;NLCD23PC;NLCD24PC;NLCD31PC;NLCD41PC;NLCD42PC;NLCD43PC;NLCD51PC;NLCD52PC;NLCD71PC;NLCD72PC;NLCD73PC;NLCD74PC;NLCD81PC;NLCD82PC;NLCD90PC;NLCD95PC")

