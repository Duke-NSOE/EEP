# DATA_PrepData.py
#
# Creates a geodatabase and extracts the base data for a user specified HUC6 into
#   a user specified Geodatabase. Data are extracted from SDE connection files and
#   clipped to the NHD Catchments within the specified HUC6.
#
# This LOCAL version pulls data from file geodatabases, replicated from the Server
#   geodatabases. 
#
# Fall 2015
# John.Fay@duke.edu

import sys, os, arcpy
arcpy.CheckOutExtension("spatial")

# Path variables
dataPth = os.path.abspath(sys.path[0]+ "\\..\\Data")

# Program variables
WBD_HUC6 = os.path.join(dataPth,"NHD.gdb","WBDHU6")
WBD_Snapshot = os.path.join(dataPth,"NHD.gdb","NationalWBDSnapshot")
NHD_Flowlines = os.path.join(dataPth,"NHD.gdb","NHDFlowlines")
NHD_CatchPolys = os.path.join(dataPth,"NHD.gdb","CatchmentFeatures")
Elev_cm = os.path.join(dataPth,"NHDrasters","ELEV_CM.img")
NHD_fdr = os.path.join(dataPth,"NHDrasters","FDR.img")
NHD_fdrnull = os.path.join(dataPth,"NHDrasters","FDRNULL.img")
NHD_cat = os.path.join(dataPth,"NHDrasters","CAT.img")
NLCD_cov = os.path.join(dataPth,"NLCDdata","nlcd_2011_landcover.img")
NLCD_canopy = os.path.join(dataPth,"NLCDdata","nlcd_2011_treecanopy_analytical.img\\Layer_1")
NLCD_imperv = os.path.join(dataPth,"NLCDdata","nlcd_2011_impervious.img")
outCoordSys = arcpy.SpatialReference(102039) #-->USA_Contiguous_Albers_Equal_Area_Conic_USGS_version

# Input variables
HUC_ID = arcpy.GetParameterAsText(0)#'030501'

# Environment variables
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = Elev_cm
arcpy.env.cellSize = Elev_cm
arcpy.env.outputCoordinateSystem = outCoordSys

# ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)

# ---Procedures---
# Create a new geodatabase in the Data folder
## Set the name
outGDB = "EEP_"+HUC_ID + ".gdb"
outGDBPth = os.path.join(dataPth,outGDB)
## Check to see that the database doesn't already exist; exit if it does
if os.path.exists(outGDBPth):
    msg(outGDBPth + " already exists.","warning")
    #sys.exit()
else: ## Create the output geodatabase
    msg("Creating output geodatabase: " + outGDB)
    arcpy.CreateFileGDB_management(dataPth,outGDB)
    outGDB = arcpy.SetParameterAsText(1,outGDBPth)

# Select and project NHD features
arcpy.env.workspace = outGDBPth
## WDB HUC6
msg("Selecting HUC6 feature from WBD")
selRecs = arcpy.Select_analysis(WBD_HUC6,"in_memory/tmpFC","HUC6 = '{}'".format(HUC_ID))
msg(" Projecting HUC6 feature --> HUC6")
arcpy.Project_management(selRecs,"HUC6",outCoordSys)
msg(" Updating metadata")
arcpy.MetadataImporter_conversion(WBD_HUC6,"HUC6")
arcpy.SetParameterAsText(2,os.path.join(outGDBPth,"HUC6"))
arcpy.Delete_management("in_memory/tmpFC")

## WDB Snapshot (HUC12)
msg("Selecting HUC12 features from WBD Snapshot")
selRecs = arcpy.Select_analysis(WBD_Snapshot,"in_memory/tmpFC","HUC_12 LIKE '{}%'".format(HUC_ID))
msg(" Projecting HUC12 features --> HUC12")
arcpy.Project_management(selRecs,"HUC12",outCoordSys)
msg(" Updating metadata")
arcpy.MetadataImporter_conversion(WBD_Snapshot,"HUC12")
arcpy.SetParameterAsText(3,os.path.join(outGDBPth,"HUC12"))
arcpy.Delete_management("in_memory/tmpFC")

## NHD Flowlines
msg("Selecting Flowline features from NHD+ v.2 --> NHDFlowlines")
selRecs = arcpy.Select_analysis(NHD_Flowlines,"in_memory/tmpFC","REACHCODE LIKE '{}%'".format(HUC_ID))
msg(" Projecting Flowline features")
arcpy.Project_management(selRecs,"NHDFlowlines",outCoordSys)
msg(" Updating metadata")
arcpy.MetadataImporter_conversion(NHD_Flowlines,"NHDFlowlines")
arcpy.SetParameterAsText(4,os.path.join(outGDBPth,"NHDFlowlines"))
arcpy.Delete_management("in_memory/tmpFC")

## NHD Flowline midpoints
msg("Creating flowline midpoint feature class --> FlowlineMidPts")
arcpy.FeatureVerticesToPoints_management("NHDFlowlines","FlowlineMidPts","MID")
arcpy.SetParameterAsText(5,os.path.join(outGDBPth,"FlowlineMidPts"))

## NHD Catchments
msg("Creating layer of NHD Catchments...")
CatchLyr = arcpy.MakeFeatureLayer_management(NHD_CatchPolys,"Catchments")
msg(" Selecting Catchments centered in the selected HUC 6")
arcpy.SelectLayerByLocation_management(CatchLyr,"INTERSECT","NHDFlowlines")
msg(" Projecting Catchment features --> NHDCatchments")
selRecs = arcpy.CopyFeatures_management(CatchLyr,"in_memory/tmpFC")
arcpy.Project_management(selRecs,"NHDCatchments",outCoordSys)
msg(" Updating metadata")
arcpy.MetadataImporter_conversion(NHD_CatchPolys,"NHDCatchments")
arcpy.SetParameterAsText(6,os.path.join(outGDBPth,"NHDCatchments"))
arcpy.Delete_management("in_memory/tmpFC")

## Mask Polygon
msg("Creating mask polygon from dissolved catchments...")
arcpy.Dissolve_management("NHDCatchments","MaskPoly")
msg(" Setting analysis extent to mask polygon")
arcpy.env.extent = "MaskPoly"
arcpy.SetParameterAsText(7,os.path.join(outGDBPth,"MaskPoly"))
arcpy.Delete_management("in_memory/tmpFC")

## Mask Raster
msg("Creating mask raster from mask poly...")
mask = arcpy.PolygonToRaster_conversion("MaskPoly","OBJECTID","Mask","CELL_CENTER","NONE",30)
arcpy.SetParameterAsText(8,os.path.join(outGDBPth,"Mask"))

## Extract source rasters by the Mask raster
msg("Extracting rasters. This can take a while...")
# Make a list of input/output pairs
rasterList = ((Elev_cm,"Elev_cm"),
              (NHD_fdr,"flowdir"),
              (NHD_fdrnull,"fdrnull"),
              (NHD_cat,"cat"),
              (NLCD_cov,"nlcd_2011"),
              (NLCD_canopy,"canopycov"),
              (NLCD_imperv,"impervious"))
# Status counter
x = 1
# Loop through the values...
for (inRas,outRas) in rasterList:
    msg("  Extracting {} ({} of 7)".format(inRas,x))
    # Check to see whether the raster exists; skip if it does
    if arcpy.Exists(outRas):
        msg("  {} has already been created. Skipping".format(outRas),"warning")
        # Set the output parameter
        parameterIndex = x + 8 #(offset by the 8 outputs above)
        arcpy.SetParameterAsText(parameterIndex,os.path.join(outGDBPth,outRas))
        # Increase the counter
        x = x + 1
        #Skip to the next items in the list
        continue
    # Make a layer to avoid issues w/weird names in server datasets
    rasterLyr = arcpy.MakeRasterLayer_management(inRas,"rasterLYR")
    # Extract the inRas by the Mask created above
    msg("  Extracting data to output {}".format(outRas))
    r = arcpy.sa.ExtractByMask(rasterLyr,mask)
    # Save the output raster
    r.save(outRas)
    # Import the metadata from the source raster
    msg(" Updating metadata")
    try:
        arcpy.MetadataImporter_conversion(inRas,outRas)
    except:
        pass
    # Set the output parameter
    parameterIndex = x + 8 #(offset by the 8 outputs above)
    arcpy.SetParameterAsText(parameterIndex,os.path.join(outGDBPth,outRas))
    #Increase the counter
    x = x + 1

msg("Finished!") 
