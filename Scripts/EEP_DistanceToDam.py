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
#dataPth = os.path.abspath(sys.path[0]+ "\\..\\Data")
#NHDsde = os.path.join(dataPth,"NHD data.sde")
#NCsde = os.path.join(dataPth,"NC.sde")

# Input variables
flowlineND = arcpy.GetParameterAsText(0) #os.path.join(NHDsde,"NHD.DBO.NHDFlowlines\\NHD.DBO.NHDFlowlines_ND")
flowlinePts = arcpy.GetParameterAsText(1) #os.path.join(dataPth,"EEP_030501.gdb\\FlowlineMidPts")
damPoints = arcpy.GetParameterAsText(2) #os.path.join(NCsde,"NC.DBO.NCdams")
maskPoly = arcpy.GetParameterAsText(3) #os.path.join(dataPth,"EEP_030501.gdb\\MaskPoly")

# Output variables
outputGDB = arcpy.GetParameterAsText(4) #os.path.join(dataPth,"EEP_030501.gdb")

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

msg("Adding flowline midpoints as incidents to NA Layer...")
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

msg("Adding dam locations as facilities to NA Layer...")
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
    #solver.restrictions = []

    #Set the restriction to match the appropriate one in the flowline network dataset
    if direction == "downstream":
        msg("Restricting analysis to the downstream direction")
        solver.restrictions = ["FlowDirection"]
        outTable = os.path.join(outputGDB,"kmToDam_downstream")
        arcpy.SetParameterAsText(5,outTable)
    else:
        msg("Restricting analysis to the upstream direction")
        solver.restrictions = ["Upstream"]
        outTable = os.path.join(outputGDB,"kmToDam_upstream")
        arcpy.SetParameterAsText(6,outTable)

    msg("Locating dams in the {} direction".format(direction))
    arcpy.na.Solve(naLyr, "SKIP", "TERMINATE", "")

    msg("Extracting route information")
    routes = arcpy.SelectData_management(naLyr, "Routes")

    msg("Saving table to {}".format(outTable))
    arcpy.CopyRows_management(routes, outTable, "")

    msg("Adding COMID field to output")
    arcpy.AddField_management(outTable, "COMID", "LONG", "10", "", "", "", "NULLABLE", "NON_REQUIRED", "")

    msg("Setting COMID field values")
    arcpy.CalculateField_management(outTable, "COMID", "int(!Name![:7])", "PYTHON", "")

    msg("Adding distance field to output")
    arcpy.AddField_management(outTable,"{}Distance_km".format(direction), "FLOAT", "6", "2", "", "", "NULLABLE", "NON_REQUIRED", "")

    msg("Setting distance values")
    arcpy.CalculateField_management(outTable,"{}Distance_km".format(direction), "[Total_Length] / 1000", "VB", "")

    msg("Cleaning up fields")
    flds = []
    for f in arcpy.ListFields(outTable)[1:-2]: #Loop through all fields but first and last two
        msg("...removing {} field".format(f.name))
        arcpy.DeleteField_management(outTable, f.name)

msg("Finished...")