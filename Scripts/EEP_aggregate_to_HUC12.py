# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 10:26:24 2015

@author: jpl717
# jplovette@gmail.com
"""
#This script uses the output from EEP_zscore_and_percentile script to weight
#and aggregate NHD+v2 catchment scores to the HUC12 level
#Script output is a table with summed stats and scores for each HUC12.
#NOTE: use full path to each of the parameters

import arcpy
from arcpy import env

env.workspace = arcpy.GetParameterAsText(0) # workspace
workingDir = arcpy.GetParameterAsText(1) #working/output directory
ScoresTable = arcpy.GetParameterAsText(2) # Output table from EEP Zscore and Percentile script
Fields = arcpy.GetParameterAsText(3) # Fields which need to be weighted and aggregated to HUC12
FlowlineTable = arcpy.GetParameterAsText(4) # Flowline table/feature class with LengthKM and REACHCODE attributes
LengthKM = arcpy.GetParameterAsText(5) #LengthKM field from FlowlineTable
REACHCODE = arcpy.GetParameterAsText(6) #REACHCODE field from FlowlineTable
inJoinField = arcpy.GetParameterAsText(7) # Field to base join on from input table (COMID or FEATUREID)
joinJoinField = arcpy.GetParameterAsText(8) # Field to base join on from join table (COMID or FEATUREID)


#######################################################

arcpy.AddMessage("Converting Scores Table to GDB Table...")
arcpy.CopyRows_management(ScoresTable, (ScoresTable + "_table"))

arcpy.AddMessage("Extracting 12 Digit HUC code from REACHCODE...")
arcpy.AddField_management(FlowlineTable, "HUC12_code", "TEXT", 12, "", 12)
arcpy.CalculateField_management(FlowlineTable, "HUC12_code", "(Left([REACHCODE], 12))", "VB")

arcpy.AddMessage("Joining Stream Length and HUC 12 code to Scores Table...")
arcpy.JoinField_management((ScoresTable + "_table"), inJoinField, FlowlineTable, joinJoinField, [LengthKM, "HUC12_code"])

arcpy.AddMessage("Calculating weighted scores (score * reach length)...")
for fld in Fields.split(';'):
    arcpy.AddMessage("adding field: " + fld + "_KMweight")    
    arcpy.AddField_management((ScoresTable + "_table"), (fld + "_KMweight"), "DOUBLE")
    arcpy.AddMessage("calculating field: " + fld + "_KMweight")    
    arcpy.CalculateField_management((ScoresTable + "_table"), (fld + "_KMweight"),
                                    "(!{}! * !{}!)".format(fld, LengthKM), "PYTHON")

arcpy.AddMessage("Calculating summary statisitics for HUC 12")
stats = []
for fld in Fields.split(';'):
    stats.append([(fld + "_KMweight"), "Sum"])

stats.append([LengthKM, "Sum"])

arcpy.Statistics_analysis((ScoresTable + "_table"), (ScoresTable + "_HUC12scores"), stats, "HUC12_code")

arcpy.AddMessage("Calculating HUC 12 scores")
for fld in Fields.split(';'):
    arcpy.AddField_management((ScoresTable + "_HUC12scores"), (fld + "_HUC12_score"), "DOUBLE")
    arcpy.CalculateField_management((ScoresTable + "_HUC12scores"), (fld +"_HUC12_score"),
                                    "!{}! / !{}!".format(("SUM_" + fld + "_KMweight"), ("SUM_" + LengthKM)), "PYTHON")