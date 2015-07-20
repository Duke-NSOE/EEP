# EEP_DistanceToDam.py
#
# Description:
#   For each catchment, this calcualates the distance upstream and downstream from
#   the catchment flowline's midpoint to the nearest dam. This does so using network
#   analyses to calculate upstream and downstream closest facilities.
#
# July 2015
# John.Fay@duke.edu

import sys, os, arcpy

# Check out the NA license
arcpy.CheckOutExtension("network")
from arcpy import na

# Path variables
dataPth = os.path.abspath(sys.path[0]+ "\\..\\Data")
NHDsde = os.path.join(dataPth,"NHD data.sde")
NCsde = os.path.join(dataPth,"NC.sde")

# Input variables
flowlineND = os.path.join(NHDsde,"NHD.DBO.NHDFlowlines\\NHD.DBO.NHDFlowlines_ND")
flowlinePts = os.path.join(dataPth,"EEP_030501.gdb\\FlowlineMidPts")
damPoints = os.path.join(NCsde,"NC.DBO.NCdams")
maskPoly = os.path.join(dataPth,"EEP_030501.gdb\\MaskPoly")

# Output variables
downstreamFC = os.path.join(dataPth,"EEP_030501.gdb\\downstreamDam")

# Script variables

# Environment variables
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


# ---Processes---
msg("Selecting dams within the catchments")
damsInHUC6 = arcpy.MakeFeatureLayer_management(damPoints,"damsInHUC6")
arcpy.SelectLayerByLocation_management(damsInHUC6,"INTERSECT",maskPoly)

msg("Creating Network Analysis Layer")
naLyr = arcpy.na.MakeClosestFacilityLayer(flowlineND,"naLyr","Length",
                                          "TRAVEL_TO","",1,"", "NO_UTURNS",
                                          "FlowDirection", "NO_HIERARCHY", "",
                                          "NO_LINES", "", "NOT_USED")

msg("Adding flowline midpoints as incidents to NA Layer")
arcpy.AddLocations_na(naLyr,"Incidents", flowlinePts,
                      "Name COMID #",
                      "0 Meters", "",
                      "NHD.DBO.NHDFlowlines SHAPE;NHD.DBO.NHDFlowlines_ND_Junctions NONE",
                      "MATCH_TO_CLOSEST",
                      "CLEAR",
                      "NO_SNAP",
                      "5 Meters",
                      "INCLUDE",
                      "NHD.DBO.NHDFlowlines #;NHD.DBO.NHDFlowlines_ND_Junctions #")

msg("Adding dam locations as facilities to NA Layer")
arcpy.AddLocations_na(naLyr, "Facilities", damsInHUC6,
                      "Name Name #;SourceID SourceID #;SourceOID SourceOID #;PosAlong PosAlong #;SideOfEdge SideOfEdge #",
                      "0 Meters",
                      "Name",
                      "NHD.DBO.NHDFlowlines SHAPE;NHD.DBO.NHDFlowlines_ND_Junctions NONE",
                      "PRIORITY", "CLEAR",
                      "NO_SNAP", "5 Meters", "INCLUDE",
                      "NHD.DBO.NHDFlowlines #;NHD.DBO.NHDFlowlines_ND_Junctions #")

msg("Solving...")
arcpy.na.Solve(naLyr, "SKIP", "TERMINATE", "")

msg("Extracting locations")
arcpy.SelectData_management(naLyr, "Routes")

msg("Saving locations to disk")
arcpy.CopyRows_management(na_Lyr+"\\Routes", downstreamFC, "")

msg("Adding COMID field to output")
arcpy.AddField_management(downstreamFC, "COMID", "LONG", "10", "", "", "", "NULLABLE", "NON_REQUIRED", "")

msg("Setting COMID field values")
arcpy.CalculateField_management(downstreamFC, "COMID", "int(!Name![:7])", "PYTHON", "")

msg("Adding distance field to output")
arcpy.AddField_management(downstreamFC, "Downstream2Dam_km", "FLOAT", "6", "2", "", "", "NULLABLE", "NON_REQUIRED", "")

msg("Setting distance values")
arcpy.CalculateField_management(downstreamFC, "Downstream2Dam_km", "[Total_Length] / 1000", "VB", "")

msg("Cleaning up fields")
flds = []
for f in arcpy.ListFields(downstreamFC)[:-2]:
    msg("Removing {} field".format(f))
    arcpy.DeleteField_management(downstreamFC, f.name)