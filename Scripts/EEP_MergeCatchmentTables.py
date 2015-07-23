# EEP_MergeCatchmentTables
#
# Joins all the tables created by the catchment models into a single, master table
#
# May 2015
# John.Fay@duke.du

import os, arcpy

# Input variables:
NHDCatchments = arcpy.GetParameterAsText(0)
NHDFlowlines = arcpy.GetParameterAsText(1)
Landscape_Stats = arcpy.GetParameterAsText(2)
FlowlineLULC = arcpy.GetParameterAsText(3)
ShadeStats = arcpy.GetParameterAsText(4)
StreamTemp = arcpy.GetParameterAsText(5)
RiparianStats = arcpy.GetParameterAsText(6)
RoadXings = arcpy.GetParameterAsText(7)
HabitatTable = arcpy.GetParameterAsText(8)
CanopyImpervTable = arcpy.GetParameterAsText(9)
AnimalOpsTable = arcpy.GetParameterAsText(10)
NPDESTable = arcpy.GetParameterAsText(11)
DownstreamDams = arcpy.GetParameterAsText(12)
UpstreamDams = arcpy.GetParameterAsText(13)
HydricSoils = arcpy.GetParameterAsText(14)

# Output variables:
outputFC = arcpy.GetParameterAsText(15)

# Set environment variables
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

def makeFldString(tbl):
    '''Makes a string of all fields in a table'''
    fldString = ""
    for f in arcpy.ListFields(tbl):
        if not f.name in ("COMID","OBJECTID"):
            fldString += "; {}".format(f.name)
    return fldString #return all but the last semicolon

# Copy the catchment feature class
msg("Creating output catchment feature class")
arcpy.Select_analysis(NHDCatchments, outputFC,"")

# Create attribute indices
msg("Creating attribute indices for faster processing")
arcpy.AddIndex_management(outputFC,"GRIDCODE;FEATUREID","TagIndex","UNIQUE","NON_ASCENDING")

# Status counters
currentCount = 1
totalCount = 14

# Process: Join Field (REDUNDANT)
msg(" Joining Reachcodes...{}/{}".format(currentCount,totalCount)); currentCount += 1
#arcpy.JoinField_management(outputFC, "FEATUREID", NHDFlowlines,"COMID","REACHCODE")

# Process: Join Field
msg(" Joining NHD Variable Table...{}/{}".format(currentCount,totalCount)); currentCount += 1
fldString = makeFldString(HabitatTable)
arcpy.JoinField_management(outputFC, "FEATUREID", HabitatTable, "COMID",fldString)
#"LENGTHKM;REACHCODE;WBAREACOMI;FTYPE;FCODE;StreamOrde;Pathlength;ArbolateSu;TotDASqKM;SLOPE;Q0001E;V0001E;Qincr0001E;TEMP0001;PPT0001;PET0001;QLOSS0001;TempV;PrecipV;RunOffV;MinMonthly;NLCD11P;NLCD12P;NLCD21P;NLCD22P;NLCD23P;NLCD24P;NLCD31P;NLCD41P;NLCD42P;NLCD43P;NLCD51P;NLCD52P;NLCD71P;NLCD72P;NLCD73P;NLCD74P;NLCD81P;NLCD82P;NLCD90P;NLCD95P;NLCD11PC;NLCD12PC;NLCD21PC;NLCD22PC;NLCD23PC;NLCD24PC;NLCD31PC;NLCD41PC;NLCD42PC;NLCD43PC;NLCD51PC;NLCD52PC;NLCD71PC;NLCD72PC;NLCD73PC;NLCD74PC;NLCD81PC;NLCD82PC;NLCD90PC;NLCD95PC")

# Process: Join Field 
msg(" Joining Landscape Stats...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "GRIDCODE", Landscape_Stats, "COMID", "runoff_SUM;flooding_SUM;slope_MEAN;road_density_MEAN;tfactor_MEAN;water_table_MEAN;erodability_MEAN;wetlands_SUM;surface_water_SUM;flood_risk_SUM")

# Process: Join Field
msg(" Joining FlowlineLULC...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "GRIDCODE", FlowlineLULC, "GRIDCODE", "FLNLCD_1;FLNLCD_2;FLNLCD_3;FLNLCD_4;FLNLCD_5;FLNLCD_7;FLNLCD_8;FLNLCD_9")

# Process: Join Field
msg(" Joining RiparianStats...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "GRIDCODE", RiparianStats, "VALUE", "Riparian_1A;Riparian_2A;Riparian_3A;Riparian_4A;Riparian_5A;Riparian_7A;Riparian_8A;Riparian_9A;Riparian_1P;Riparian_2P;Riparian_3P;Riparian_4P;Riparian_5P;Riparian_7p;Riparian_8P;Riparian_9P;")

# Process: Join Field
msg(" Joining Shadestats...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", ShadeStats, "COMID", "ShadedSegments;ShadedLength;LongestSegment;MeanShadeLength")

# Process: Join Field
msg(" Joining Streamtemp...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", StreamTemp, "FEATUREID", "cold;cool;warm;TotLength")

# Process: Join Field
msg(" Joining RoadXings...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", RoadXings, "COMID", "Crossings")

# Process: Join Field
msg(" Joining Canopy and Impervious Stats...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "GRIDCODE", CanopyImpervTable, "COMID", "PctCanopy;PctImpervious")

# Process: Join Field
msg(" Joining AnimalOpsCount...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", AnimalOpsTable, "FEATUREID", "AnimalOps")

# Process: Join Field
msg(" Joining NPDESCount...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", NPDESTable, "FEATUREID", "NPDES")

# Process: Join Field
msg(" Joining downstream dam distance...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", DownstreamDams, "COMID","downstreamDistance_km")

# Process: Join Field
msg(" Joining downstream dam distance...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", UpstreamDams, "COMID","upstreamDistance_km")

# Process: Join Field
msg(" Joining hydric soils...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", HydricSoils, "FEATUREID","PCT_HYDRIC;AREA_HYDRIC")

# Process: Fix Null Values
flds = arcpy.ListFields(outputFC)
for fld in flds[8:]: #Skip the first 8 fields as they are ok
    #msg("Searching for null values in {}...".format(fld.name))
    #Select records where value is null
    lyr = arcpy.MakeFeatureLayer_management(outputFC, "LYR", "{} IS Null".format(fld.name))
    #Get the number of records to fix
    NullCount =  arcpy.GetCount_management("Lyr").getOutput(0)
    if int(NullCount) > 0:
        msg("Fixing {} null records {}".format(NullCount, fld.name))
        #Depending on the field, set missing values to -9999 or 0
        if fld.name in ("warm","cold","cool","TotLength","Crossings","AnimalOps","NPDES","PCT_HYDRIC","AREA_HYDRIC") or \
           "NLCD" in fld.name or \
           "Shade" in fld.name:
            arcpy.CalculateField_management("Lyr",fld.name,"0")
        else:
            arcpy.CalculateField_management("Lyr",fld.name,"-9999")
    
msg("Finished!")