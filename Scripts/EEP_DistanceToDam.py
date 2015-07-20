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
outputGDB = os.path.join(dataPth,"EEP_030501.gdb")

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
naLyr = arcpy.na.MakeClosestFacilityLayer(flowlineND,
                                          "naLyr",      # network dataset layer name
                                          "Length",     # impedance attributed; go for nearest dam
                                          "TRAVEL_TO",  # travel *downstream* to dam
                                          "",1,"",      # no cutoff; find 1 dam; no attribute accumulators
                                          "NO_UTURNS",  # no uturns
                                          "FlowDirection",   # restrict flow to the downstream direction
                                          "NO_HIERARCHY","", # don't use any hierarchy
                                          "NO_LINES",        # don't create any output lines
                                          "", "NOT_USED")    # ignore time of day

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

msg("Creating the solver object")
solver = na.GetSolverProperties(naLyr.getOutput(0))

##Loop through downstream and upstream search
for direction in ("downstream","upstream"):

    #Clear all restrictions
    solver.restrictions = []

    #Set the restriction to match the appropriate one in the flowline network dataset
    if direction == "downstream":
        msg("Restricting analysis to the downstream direction")
        solver.restrictions.append("FlowDirection")
        outFC = os.path.join(outputGDB,"kmToDam_downstream")
    else:
        msg("Restricting analysis to the upstream direction")
        solver.restrictions.append("Upstream")
        outFC = os.path.join(outputGDB,"kmToDam_upstream")

    msg("Locating dams in the {} direction".format(direction))
    arcpy.na.Solve(naLyr, "SKIP", "TERMINATE", "")

    msg("Extracting route information")
    routes = arcpy.SelectData_management(naLyr, "Routes")

    msg("Saving table to ".format(outFC))
    arcpy.CopyRows_management(routes, outFC, "")

    msg("Adding COMID field to output")
    arcpy.AddField_management(outFC, "COMID", "LONG", "10", "", "", "", "NULLABLE", "NON_REQUIRED", "")

    msg("Setting COMID field values")
    arcpy.CalculateField_management(outFC, "COMID", "int(!Name![:7])", "PYTHON", "")

    msg("Adding distance field to output")
    arcpy.AddField_management(outFC, "Downstream2Dam_km", "FLOAT", "6", "2", "", "", "NULLABLE", "NON_REQUIRED", "")

    msg("Setting distance values")
    arcpy.CalculateField_management(outFC, "Downstream2Dam_km", "[Total_Length] / 1000", "VB", "")

    msg("Cleaning up fields")
    flds = []
    for f in arcpy.ListFields(outFC)[1:-2]: #Loop through all fields but first and last two
        msg("...removing {} field".format(f))
        arcpy.DeleteField_management(outFC, f.name)

msg("Finished...")