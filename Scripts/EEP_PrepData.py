# EEP_PrepData.py
#
# Creates a geodatabase and extracts the base data for a user specified HUC6 into
#   a user specified Geodatabase. Data are extracted from SDE connection files and
#   clipped to the NHD Catchments within the specified HUC6.
#
# REQUIRES the <NHD data.sde> and <NLCD data.sde> SDE connection files in the data
#    folder. Currently these only work on machines with firewall access on the NS-GIS
#    server. Plans are to move these to an ArcGIS online portal. 
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy
arcpy.CheckOutExtension("spatial")

# Path variables
dataPth = os.path.abspath(sys.path[0]+ "\\..\\Data")

# Program variables
WBD_HUC6 = os.path.join(dataPth,"NHD data.sde","NHDplusV2.SDE.WBDHU6")
WBD_Snapshot = os.path.join(dataPth,"NHD data.sde","NHDplusV2.DBO.NationalWBDSnapshot")
NHD_Flowlines = os.path.join(dataPth,"NHD data.sde","NHDplusV2.SDE.NHDFlowline")
NHD_CatchPolys = os.path.join(dataPth,"NHD data.sde","NHDplusV2.SDE.CatchmentFeatures")
Elev_cm = os.path.join(dataPth,"NHD data.sde","NHDplusV2.SDE.elev_cm")
NHD_fdr = os.path.join(dataPth,"NHD data.sde","NHDplusV2.SDE.fdr")
NHD_fdrnull = os.path.join(dataPth,"NHD data.sde","NHDplusV2.SDE.fdrnull")
NHD_cat = os.path.join(dataPth,"NHD data.sde","NHDplusV2.SDE.cat")
NLCD_cov = os.path.join(dataPth,"NLCD data.sde","USdata.DBO.nlcd_2011")
NLCD_canopy = os.path.join(dataPth,"NLCD data.sde","USdata.DBO.nlcd2011_usfs_treecanopy_analytical_3_31_2014\\Band_1")
NLCD_imperv = os.path.join(dataPth,"NLCD data.sde","USdata.DBO.nlcd_2011_impervious_2011_edition_2014_03_31")
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
## Check to see that the datbase doesn't already exist; exit if it does
if os.path.exists(outGDBPth):
    msg(outGDBPth + " already exists.\nExiting.","error")
    sys.exit()
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
arcpy.ImportMetadata_conversion(WBD_HUC6,"FROM_ARCGIS","HUC6","ENABLED")
arcpy.SetParameterAsText(2,os.path.join(outGDBPth,"HUC6"))

## WDB Snapshot (HUC12)
msg("Selecting HUC12 features from WBD Snapshot")
selRecs = arcpy.Select_analysis(WBD_Snapshot,"in_memory/tmpFC","HUC_12 LIKE '{}%'".format(HUC_ID))
msg(" Projecting HUC12 features --> HUC12")
arcpy.Project_management(selRecs,"HUC12",outCoordSys)
msg(" Updating metadata")
arcpy.ImportMetadata_conversion(WBD_Snapshot,"FROM_ARCGIS","HUC12","ENABLED")
arcpy.SetParameterAsText(3,os.path.join(outGDBPth,"HUC12"))

## NHD Flowlines
msg("Selecting Flowline features from NHD+ v.2 --> NHDFlowlines")
selRecs = arcpy.Select_analysis(NHD_Flowlines,"in_memory/tmpFC","REACHCODE LIKE '{}%'".format(HUC_ID))
msg(" Projecting Flowline features")
arcpy.Project_management(selRecs,"NHDFlowlines",outCoordSys)
msg(" Updating metadata")
arcpy.ImportMetadata_conversion(NHD_Flowlines,"FROM_ARCGIS","NHDFlowlines","ENABLED")
arcpy.SetParameterAsText(4,os.path.join(outGDBPth,"NHDFlowlines"))

## NHD Flowline midpoints
msg("Creating flowline midpoint feature class --> FlowlineMidPts")
arcpy.FeatureVerticesToPoints_management("NHDFlowlines","FlowlineMidPts","MID")
arcpy.SetParameterAsText(5,os.path.join(outGDBPth,"FlowlineMidPts"))

## NHD Catchments
msg("Creating layer of NHD Catchments...")
CatchLyr = arcpy.MakeFeatureLayer_management(NHD_CatchPolys,"Catchments")
msg(" Selecting Catchments centered in the selected HUC 6")
arcpy.SelectLayerByLocation_management(CatchLyr,"HAVE_THEIR_CENTER_IN","HUC6")
msg(" Projecting Catchment features --> NHDCatchments")
selRecs = arcpy.CopyFeatures_management(CatchLyr,"in_memory/tmpFC")
arcpy.Project_management(selRecs,"NHDCatchments",outCoordSys)
msg(" Updating metadata")
arcpy.ImportMetadata_conversion(NHD_CatchPolys,"FROM_ARCGIS","NHDCatchments","ENABLED")
arcpy.SetParameterAsText(6,os.path.join(outGDBPth,"NHDCatchments"))

## Mask Polygon
msg("Creating mask polygon from dissolved catchments...")
arcpy.Dissolve_management("NHDCatchments","MaskPoly")
msg(" Setting analysis extent to mask polygon")
arcpy.env.extent = "MaskPoly"
arcpy.SetParameterAsText(7,os.path.join(outGDBPth,"MaskPoly"))

## Mask Raster
msg("Creating mask raster from mask poly...")
mask = arcpy.PolygonToRaster_conversion("MaskPoly","OBJECTID","Mask","CELL_CENTER","NONE",30)
arcpy.SetParameterAsText(8,os.path.join(outGDBPth,"Mask"))

## Elevation
msg("Extracting rasters. This can take a while...")
msg("  Extracting NHD Elev_cm (1 of 7)")
r = arcpy.sa.ExtractByMask(Elev_cm,"Mask")
r.save("Elev_cm")
msg(" Updating metadata")
arcpy.ImportMetadata_conversion(Elev_cm,"FROM_ARCGIS","Elev_cm","ENABLED")
arcpy.SetParameterAsText(9,os.path.join(outGDBPth,"Elev_cm"))

## FlowDir
msg("  Extracting NHD FlowDir (2 of 7)")
r = arcpy.sa.ExtractByMask(NHD_fdr,"mask")
r.save("flowdir")
msg(" Updating metadata")
arcpy.ImportMetadata_conversion(NHD_fdr,"FROM_ARCGIS","flowdir","ENABLED")
arcpy.SetParameterAsText(10,os.path.join(outGDBPth,"flowdir"))

## FlowDirNull
msg("  Extracting NHD FlowDirNull (3 of 7)")
r = arcpy.sa.ExtractByMask(NHD_fdrnull,"mask")
r.save("fdrnull")
msg(" Updating metadata")
arcpy.ImportMetadata_conversion(NHD_fdrnull,"FROM_ARCGIS","fdrnull","ENABLED")
arcpy.SetParameterAsText(11,os.path.join(outGDBPth,"fdrnull"))

## Cat
msg("  Extracting NHD Catchment raster (4 of 7)")
r = arcpy.sa.ExtractByMask(NHD_cat,"mask")
r.save("cat")
msg(" Updating metadata")
arcpy.ImportMetadata_conversion(NHD_cat,"FROM_ARCGIS","cat","ENABLED")
arcpy.SetParameterAsText(12,os.path.join(outGDBPth,"cat"))

## NLCD
msg("  Extracting NLCD land cover (5 of 7)")
r = arcpy.sa.ExtractByMask(NLCD_cov,"mask")
r.save("nlcd_2011")
msg(" Updating metadata")
arcpy.ImportMetadata_conversion(NLCD_cov,"FROM_ARCGIS","nlcd_2011","ENABLED")
msg(" Updating colormap")
arcpy.AddColormap_management("nlcd_2011",NLCD_cov)
arcpy.SetParameterAsText(13,os.path.join(outGDBPth,"nlcd_2011"))

## Canopy Cover
msg("  Extracting NLCD canopy cover (6 of 7)")
r = arcpy.sa.ExtractByMask(NLCD_canopy,"mask")
r.save("canopycov")
msg(" Updating metadata")
arcpy.ImportMetadata_conversion(NLCD_canopy,"FROM_ARCGIS","canopycov","ENABLED")
arcpy.SetParameterAsText(14,os.path.join(outGDBPth,"canopycov"))

## Impervious
msg("  Extracting NLCD impervious (7 of 7)")
r = arcpy.sa.ExtractByMask(NLCD_imperv,"mask")
r.save("impervious")
msg(" Updating metadata")
arcpy.ImportMetadata_conversion(NLCD_imperv,"FROM_ARCGIS","impervious","ENABLED")
msg(" Updating colormap")
arcpy.AddColormap_management("impervious",NLCD_imperv)
arcpy.SetParameterAsText(15,os.path.join(outGDBPth,"impervious"))

msg("Finished!") 
