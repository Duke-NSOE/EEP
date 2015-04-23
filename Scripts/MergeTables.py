#----------------------------------------------------------------------------------
# MergeTables.py
#
# Joins all the tables created by the catchment models into a sigle, master table
#
# March 20, 2015
# John.Fay@dukee.du
#----------------------------------------------------------------------------------

import os, arcpy

# HUC GDB
HUC_GDB = arcpy.GetParameterAsText(0) #'C:\\Temp\\EEP_March20th\\Data\\EEP_030501.gdb'
OutTable = arcpy.GetParameterAsText(1) #os.path.join(HUC_GDB,"AllAttribs")

# Set the workspace
arcpy.env.workspace = HUC_GDB

# Local variables:
Landscape_Stats = "LandscapeStats"
FlowlineNLCD = "FlowlineNLCD"
RiparianStats = "RiparianStats"
ShadeStats = "ShadeStats"
HabitatTable = "HabitatTable"
GeologyTable = "GeologyTable"
StreamTemp = "StreamTemp"
NPDESCount = "NPDESCount"
AnimalOpsCount = "AnimalOpsCount"
RoadXings = "RoadXings"
NHDCatchments = "NHDCatchments"
AllAttriibutes = "AllAttriibutes"

#msg function
def msg(txt):
    print txt
    arcpy.AddMessage(txt)
    return

# Process: Select
msg("Creating catchment feature class")
arcpy.Select_analysis(NHDCatchments, OutTable,"")

# Process: Join Field
msg(" Joining Habitat Table...1/10")
arcpy.JoinField_management(OutTable, "FEATUREID", HabitatTable, "COMID", "LENGTHKM;REACHCODE;WBAREACOMI;FTYPE;FCODE;StreamOrde;Pathlength;ArbolateSu;AreaSqKM;TotDASqKM;SLOPE;Q0001E;V0001E;Qincr0001E;TEMP0001;PPT0001;PET0001;QLOSS0001;Q0001E_01;Q0001E_02;Q0001E_03;Q0001E_04;Q0001E_05;Q0001E_06;Q0001E_07;Q0001E_08;Q0001E_09;Q0001E_10;Q0001E_11;Q0001E_12;TempV;PrecipV;RunOffV;MinMonthly;NLCD11P;NLCD12P;NLCD21P;NLCD22P;NLCD23P;NLCD24P;NLCD31P;NLCD41P;NLCD42P;NLCD43P;NLCD51P;NLCD52P;NLCD71P;NLCD72P;NLCD73P;NLCD74P;NLCD81P;NLCD82P;NLCD90P;NLCD95P;NLCD11PC;NLCD12PC;NLCD21PC;NLCD22PC;NLCD23PC;NLCD24PC;NLCD31PC;NLCD41PC;NLCD42PC;NLCD43PC;NLCD51PC;NLCD52PC;NLCD71PC;NLCD72PC;NLCD73PC;NLCD74PC;NLCD81PC;NLCD82PC;NLCD90PC;NLCD95PC")

# Process: Join Field (2)
msg(" Joining Landscape Stats...2/10")
arcpy.JoinField_management(OutTable, "GRIDCODE", Landscape_Stats, "COMID", "FEATUREID;runoff_SUM;flooding_SUM;slope_MEAN;road_density_MEAN;tfactor_MEAN;water_table_MEAN;erodability_MEAN;wetlands_SUM;surface_water_SUM;flood_risk_SUM")

# Process: Join Field (3)
msg(" Joining FlowlineNLCD...3/10")
arcpy.JoinField_management(OutTable, "GRIDCODE", FlowlineNLCD, "VALUE", "VALUE_11;VALUE_21;VALUE_22;VALUE_23;VALUE_24;VALUE_31;VALUE_41;VALUE_42;VALUE_43;VALUE_52;VALUE_71;VALUE_81;VALUE_82;VALUE_90;VALUE_95")

# Process: Join Field (4)
msg(" Joining RiparianStats...4/10")
arcpy.JoinField_management(OutTable, "GRIDCODE", RiparianStats, "VALUE", "AreaRiparian;PctRipForest;PctRipWetland")

# Process: Join Field (5)
msg(" Joining Shadestats...5/10")
arcpy.JoinField_management(OutTable, "FEATUREID", ShadeStats, "COMID", "ShadedFragments;ShadedLength;LongestShade;MeanShadeLength")

# Process: Join Field (6)
msg(" Joining Streamtemp...6/10")
arcpy.JoinField_management(OutTable, "FEATUREID", StreamTemp, "FEATUREID", "cold;cool;warm;TotLength")

# Process: Join Field (8)
msg(" Joining Geology...7/10")
arcpy.JoinField_management(OutTable, "FEATUREID", GeologyTable, "COMID", "TYPE")

# Process: Join Field (7)
msg(" Joining RoadXings...8/10")
arcpy.JoinField_management(OutTable, "FEATUREID", RoadXings, "COMID", "Crossings")

# Process: Join Field (9)
msg(" Joining AnimalOpsCount...9/10")
arcpy.JoinField_management(OutTable, "FEATUREID", AnimalOpsCount, "FEATUREID", "AnimalOpsCount")

# Process: Join Field (10)
msg(" Joining NPDESCount...10/10")
arcpy.JoinField_management(OutTable, "FEATUREID", NPDESCount, "FEATUREID", "NPDESCount")

# Process: Fix Null Values
flds = arcpy.ListFields(OutTable)
for fld in flds[8:]: #Skip the first 8 fields as they are ok
    msg("Fixing null values in {}...".format(fld.name))
    #Select records where value is null
    lyr = arcpy.MakeFeatureLayer_management(OutTable, "LYR", "{} IS Null".format(fld.name))
    #Get the number of records to fix
    NullCount =  arcpy.GetCount_management("Lyr").getOutput(0)
    if int(NullCount) > 0:
        msg("{} records to fix in {}".format(NullCount, fld.name))
        #Set selected records to 0
        arcpy.CalculateField_management("Lyr",fld.name,"0")
    
