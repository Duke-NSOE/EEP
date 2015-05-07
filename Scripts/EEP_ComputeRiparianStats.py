# EEP_ComputeRiparianStats.py
#
# Description:
#   Computes areas within 1m of elevation above stream cells in a given NHD
#   catchment and calculates the amount and percentages of forest and wetland
#   cover types, as determined by NLCD 2011 land cover. 
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy
from arcpy import sa
arcpy.CheckOutExtension("spatial")

# Input variables
zThreshold = arcpy.GetParameterAsText(0)
catchRaster = arcpy.GetParameterAsText(1)
elevRaster = arcpy.GetParameterAsText(2)
fldrRaster = arcpy.GetParameterAsText(3)
fdrnullRaster = arcpy.GetParameterAsText(4)
nlcdRaster = arcpy.GetParameterAsText(5)

# Output variables
riparianTbl = arcpy.GetParameterAsText(6)
riparianRaster = arcpy.GetParameterAsText(7)

# Script variables
zonalForestTbl = "in_memory/ZonalForest"
zonalWetlandTbl = "in_memory/ZonalWetland"

# Environment variables
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = fldrRaster
arcpy.env.cellSize = fldrRaster

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
## Create a raster of stream cells, with values set to elevation
msg("Creating a streams raster (inverting NHD FlowDirNull Raster")
strmRaster = sa.IsNull(fdrnullRaster)

msg("Assigning elevation values to stream cells")
strmElevRaster = sa.Con(strmRaster,elevRaster)

msg("Calculating watersheds labeled with elevation")
elevSheds = sa.Watershed(fdrnullRaster,strmElevRaster)

msg("Identifying cells within {}m in elevation from stream cell")
elevDiff = sa.Minus(elevRaster,elevSheds)

msg("Extracting land cover within riparian cells")
riparianNLCD = sa.SetNull(elevDiff,nlcdRaster,'VALUE > {}'.format(zThreshold))

## If name is given for riparian raster, save it
if not(riparianRaster == "" or riparianRaster == "#"):
    msg("Saving riparian NLCD raster to {}".format(riparianRaster))
    riparianNLCD.save(riparianRaster)

msg("Determining area of forest and wetland within riparian zone")
msg("...creating riparian forest raster")
forestRaster = sa.Con(riparianNLCD,1,0,'VALUE IN (41, 42, 43)')
msg("...updating riparian wetland cells")
forWetRaster = sa.Con(riparianNLCD,2,forestRaster,'VALUE IN (90, 95)')
msg("...tabulating area of forest, wetland, and other in each catchment")
sa.TabulateArea(catchRaster,"VALUE",forWetRaster,"VALUE",riparianTbl)

msg("...updating field names")
arcpy.AlterField_management(riparianTbl,"VALUE","GRIDCODE","GRIDCODE")
arcpy.AlterField_management(riparianTbl,"VALUE_0","Other","Other lulc")
arcpy.AlterField_management(riparianTbl,"VALUE_1","Forest","Riparian forest")
arcpy.AlterField_management(riparianTbl,"VALUE_2","Wetland","Riparian wetland")

msg("Calculating percentages")
msg("...forest")
arcpy.AddField_management(riparianTbl,"pctForest","DOUBLE",5,2,8,"Pct riparian forest")
arcpy.CalculateField_management(riparianTbl,"pctForest","([Forest] / ( [Forest] + [Wetland] + [Other])) * 100", "VB",  "#")

msg("...wetland")
arcpy.AddField_management(riparianTbl,"pctWetland","DOUBLE",5,2,8,"Pct riparian wetland")
arcpy.CalculateField_management(riparianTbl,"pctWetland","([Wetland] / ( [Forest] + [Wetland] + [Other])) * 100", "VB",  "#")

msg("Finished!")


