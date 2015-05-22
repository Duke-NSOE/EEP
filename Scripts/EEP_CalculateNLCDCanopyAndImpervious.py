# EEP_CalculateNLCDCanopyAndImpervious.py
#
# Description: Determines the percent canopy cover and percent developed impervious
#  surface of each catchment using the NLCD data. 
#
# Spring 2015
# John.Fay@duke.edu

# Import arcpy module
import sys, os, arcpy

#import sys, os, arcpy
arcpy.CheckOutExtension("spatial")

# Inputs variables
catchRaster = arcpy.GetParameterAsText(0)
NLCD_canopy = arcpy.GetParameterAsText(1)
NLCD_imperv = arcpy.GetParameterAsText(2)
outTable = arcpy.GetParameterAsText(3)

# Environment variables
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = catchRaster
arcpy.env.cellSize = catchRaster

# Local variables:
tmpZStat = "in_memory\\zStat"

# ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)


# Create the output table
arcpy.AddMessage("Creating output table from catchment raster")
arcpy.CopyRows_management(catchRaster,outTable)
arcpy.AlterField_management(outTable,"VALUE","COMID","COMID")
arcpy.DeleteField_management(outTable,["COUNT_","SOURCEFC"])

## CANOPY COVER
# Process: Zonal Statistics as Table
arcpy.AddMessage("...Calculating percent canopy cover in each catchment")
arcpy.gp.ZonalStatisticsAsTable_sa(catchRaster, "VALUE", NLCD_canopy, tmpZStat, "DATA", "MEAN")

# Process: Change the field name from generic to something more descriptive
arcpy.AddMessage("...renaming field")
arcpy.AlterField_management(tmpZStat,"MEAN","PctCanopy")

# Process: Join Field
arcpy.AddMessage("...updating output table")
arcpy.JoinField_management(outTable,"COMID",tmpZStat,"VALUE","PctCanopy")

## PERCENT IMPERVIOUSNESS
# Process: Zonal Statistics as Table
arcpy.AddMessage("...Calculating percent impervious of each catchment")
arcpy.gp.ZonalStatisticsAsTable_sa(catchRaster, "VALUE", NLCD_imperv, tmpZStat, "DATA", "MEAN")

# Process: Change the field name from generic to something more descriptive
arcpy.AddMessage("...renaming field")
arcpy.AlterField_management(tmpZStat,"MEAN","PctImpervious")

# Process: Join Field
arcpy.AddMessage("...updating output table")
arcpy.JoinField_management(outTable,"COMID",tmpZStat,"VALUE","PctImpervious")