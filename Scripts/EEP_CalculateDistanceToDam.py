# EEP_CalculateDistanceToDam.py
# 
# Description: Calculated the distance from the center point of each flowline to the
#  nearest upstream and downstream dam. 
#
# Spring 2015
# John.Fay@duke.edu

# Import arcpy module
import os, arcpy

# Check out any necessary licenses
arcpy.CheckOutExtension("Network")

# Path variables
dataPth = os.path.abspath(sys.path[0]+ "\\..\\Data")

# Input variables:
Flowline_ND = os.path.join(dataPth,"NHD data.sde","NHDplusV2.SDE.NHDFlowline","NHDplusV2.SDE.NHDFlowline_ND")
Dams = os.path.join(dataPth,"NC.sde","nc.DBO.SC_NC_Dams")
FlowlineMidPts = arcpy.GetParameterAsTest(0)

# Output variables
damStatsTbl = arcpy.GetParameterAsText(1)

# Local variables:
Routes = "Downstream Distance to Dam\\Routes"
DownDist2Dam = "in_memory\Route2Dam"

# ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)

# Make Closest Facility Layer
msg("Setting up network analysis to determine distance to closest downstream dam")
arcpy.MakeClosestFacilityLayer_na(Flowline_ND,
                                  "Downstream Distance to Dam", "Length", "TRAVEL_TO", "",
                                  "1", "", "ALLOW_UTURNS", "Downstream", "NO_HIERARCHY", "",
                                  "TRUE_LINES_WITHOUT_MEASURES", "", "NOT_USED")

# Add flowline centerpoints as incidents in the network analysis
msg("Adding flowline centerpoints as incidents in the network analysis")
arcpy.AddLocations_na("Downstream Distance to Dam", "Incidents", FlowlineMidPts,
                      "Name COMID #", "0 Meters", "",
                      "Flowlines SHAPE;NHDFlow_ND_Junctions NONE",
                      "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters",
                      "INCLUDE", "Flowlines #;NHDFlow_ND_Junctions #")

# Add dam locations as facilities in the network analysis
msg("Adding dam locations as facilities in the network analysis")
arcpy.AddLocations_na("Downstream Distance to Dam", "Facilities", Dams,
                      "Name Name #", "50 Meters", "Name",
                      "Flowlines SHAPE;NHDFlow_ND_Junctions NONE",
                      "PRIORITY", "CLEAR", "NO_SNAP", "5 Meters",
                      "INCLUDE", "Flowlines #;NHDFlow_ND_Junctions #")

# Solve the network analysis
msg("Executing network analysis")
arcpy.Solve_na("Downstream Distance to Dam", "SKIP", "TERMINATE", "")

# Extract routes from the solved analysis
msg("Extracting route information")
arcpy.SelectData_management("Downstream Distance to Dam", "Routes")

# Process: Copy Rows
arcpy.CopyRows_management(Routes, DownDist2Dam, "")

# Process: Add Field
arcpy.AddField_management(DownDist2Dam, "FEATUREID", "LONG", "10", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
arcpy.CalculateField_management(DownDist2Dam, "FEATUREID", "int(!Name![:7])", "PYTHON", "")

# Process: Add Field (2)
arcpy.AddField_management(DownDist2Dam, "Downstream2Dam_km", "FLOAT", "6", "2", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (2)
arcpy.CalculateField_management(DownDist2Dam, "Downstream2Dam_km", "[Total_Length] / 1000", "VB", "")

# Process: Delete Field
#arcpy.DeleteField_management(DownDist2Dam, "")

# Copy to output table
msg("Saving output to {}".format(damStatsTbl))
arcpy.CopyRows_management(DownDist2Dam,damStatsTbl)

