# EEP_MergeCatchmentTables
#
# Joins all the tables created by the catchment models into a single, master table
#
# May 2015
# John.Fay@duke.du

import os, arcpy

# Input variables:
NHDCatchments = arcpy.GetParameterAsText(0)
Landscape_Stats = arcpy.GetParameterAsText(1)
FlowlineLULC = arcpy.GetParameterAsText(2)
ShadeStats = arcpy.GetParameterAsText(3)
StreamTemp = arcpy.GetParameterAsText(4)
RiparianStats = arcpy.GetParameterAsText(5)
RoadXings = arcpy.GetParameterAsText(6)
HabitatTable = arcpy.GetParameterAsText(7)
CanopyImpervTable = arcpy.GetParameterAsText(8)
AnimalOpsTable = arcpy.GetParameterAsText(9)
NPDESTable = arcpy.GetParameterAsText(10)
DownstreamDams = arcpy.GetParameterAsText(11)
UpstreamDams = arcpy.GetParameterAsText(12)
HydricSoils = arcpy.GetParameterAsText(13)

# Output variables:
outputFC = arcpy.GetParameterAsText(14)

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
totalCount = 12

# Process: Join Field
msg(" Joining Habitat Table...{}/{}".format(currentCount,totalCount)); currentCount += 1
fldString = makeFldString(HabitatTable)
arcpy.JoinField_management(outputFC, "FEATUREID", HabitatTable, "COMID",fldString)
#"LENGTHKM;REACHCODE;WBAREACOMI;FTYPE;FCODE;StreamOrde;Pathlength;ArbolateSu;TotDASqKM;SLOPE;Q0001E;V0001E;Qincr0001E;TEMP0001;PPT0001;PET0001;QLOSS0001;TempV;PrecipV;RunOffV;MinMonthly;NLCD11P;NLCD12P;NLCD21P;NLCD22P;NLCD23P;NLCD24P;NLCD31P;NLCD41P;NLCD42P;NLCD43P;NLCD51P;NLCD52P;NLCD71P;NLCD72P;NLCD73P;NLCD74P;NLCD81P;NLCD82P;NLCD90P;NLCD95P;NLCD11PC;NLCD12PC;NLCD21PC;NLCD22PC;NLCD23PC;NLCD24PC;NLCD31PC;NLCD41PC;NLCD42PC;NLCD43PC;NLCD51PC;NLCD52PC;NLCD71PC;NLCD72PC;NLCD73PC;NLCD74PC;NLCD81PC;NLCD82PC;NLCD90PC;NLCD95PC")

# Process: Join Field (2)
msg(" Joining Landscape Stats...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "GRIDCODE", Landscape_Stats, "COMID", "runoff_SUM;flooding_SUM;slope_MEAN;road_density_MEAN;tfactor_MEAN;water_table_MEAN;erodability_MEAN;wetlands_SUM;surface_water_SUM;flood_risk_SUM")

# Process: Join Field (3)
msg(" Joining FlowlineLULC...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "GRIDCODE", FlowlineLULC, "GRIDCODE",
                           "FLNLCD_11;FLNLCD_21;FLNLCD_22;FLNLCD_23;FLNLCD_24;FLNLCD_31;FLNLCD_41;FLNLCD_42;FLNLCD_43;FLNLCD_52;FLNLCD_71;FLNLCD_81;FLNLCD_82;FLNLCD_90;FLNLCD_95")

# Process: Join Field (4)
msg(" Joining RiparianStats...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "GRIDCODE", RiparianStats, "GRIDCODE", "NLCD_1A;NLCD_2A;NLCD_3A;NLCD_4A;NLCD_5A;NLCD_7A;NLCD_8A;NLCD_9A;NLCD_1P;NLCD_2P;NLCD_3P;NLCD_4P;NLCD_5P;NLCD_7p;NLCD_8P;NLCD_9P;")

# Process: Join Field (5)
msg(" Joining Shadestats...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", ShadeStats, "COMID", "ShadedSegments;ShadedLength;LongestSegment;MeanShadeLength")

# Process: Join Field (6)
msg(" Joining Streamtemp...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", StreamTemp, "FEATUREID", "cold;cool;warm;TotLength")

# Process: Join Field (7)
msg(" Joining RoadXings...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", RoadXings, "COMID", "Crossings")

# Process: Join Field (8)
msg(" Joining Canopy and Impervious Stats...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "GRIDCODE", CanopyImpervTable, "COMID", "PctCanopy;PctImpervious")

# Process: Join Field (9)
msg(" Joining AnimalOpsCount...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", AnimalOpsTable, "FEATUREID", "AnimalOps")

# Process: Join Field (10)
msg(" Joining NPDESCount...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", NPDESTable, "FEATUREID", "NPDES")

# Process: Join Field (11)
msg(" Joining downstream dam distance...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", DownstreamDams, "COMID","downstreamDistance_km")

# Process: Join Field (12) 
msg(" Joining downstream dam distance...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", UpstreamDams, "COMID","upstreamDistance_km")

# Process: Join Field (13) 
msg(" Joining hydric soils...{}/{}".format(currentCount,totalCount)); currentCount += 1
arcpy.JoinField_management(outputFC, "FEATUREID", HydricSoils, "COMID","PCT_HYDRIC;AREA_HYDRIC")

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
        if fld.name in ("warm","cold","cool","TotLength","Crossings") or \
           "NLCD" in fld.name or \
           "Shade" in fld.name:
            arcpy.CalculateField_management("Lyr",fld.name,"0")
        else:
            arcpy.CalculateField_management("Lyr",fld.name,"-9999")
    
msg("Finished!")