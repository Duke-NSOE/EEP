# EEP_ComputeFlowlineLULC.py
#
# Description:
#   Tabulates the area of different NLCD land cover classes found within stream
#   pixels of each catchment. 
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy
from arcpy import sa
arcpy.CheckOutExtension("spatial")

# Input variables
catchRaster = arcpy.GetParameterAsText(0)
nlcdRaster = arcpy.GetParameterAsText(1)
fldrnullRaster = arcpy.GetParameterAsText(2)

# Output variables
flowlineTbl = arcpy.GetParameterAsText(3)

# Environment variables
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = catchRaster
arcpy.env.cellSize = catchRaster

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
# Invert the fldirnull raster
msg("Extracting stream cells from NHD flowdir null raster")
streamRaster = sa.IsNull(fldrnullRaster)

# If pixel is a stream, set to NLCD
msg("Converting stream cells to NLCD classes") 
streamNLCD = sa.Con(streamRaster,nlcdRaster)

# Tabulate Areas
msg("Cross tabulating NLCD classes for each NHD catchment")
sa.TabulateArea(catchRaster,"VALUE",streamNLCD,"VALUE",flowlineTbl)

# Rename fields
msg("Renaming fields...")
msg("  setting VALUE to GRIDCODE")
arcpy.AlterField_management(flowlineTbl,"VALUE","GRIDCODE","GRIDCODE")
for nlcdClass in [11,21,22,23,24,31,41,42,43,52,71,81,82,90,95]:
    fldName = "VALUE_{}".format(nlcdClass)
    outName = "FLNLCD_{}".format(nlcdClass)
    msg("  setting {} to {}".format(fldName, outName))
    arcpy.AlterField_management(flowlineTbl,fldName, outName, outName)

msg("Finished!")
