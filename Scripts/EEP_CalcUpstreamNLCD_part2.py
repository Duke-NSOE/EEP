# EEP_CalcUpstreamNLCD_part2.py
#
# Description: Merges the upland accumulated rasters into a single table
#
# Dec 2014, john.fay@duke.edu

import sys, os, arcpy
from arcpy import env
from arcpy.sa import *

env.overwriteOutput = True

#Check out the SA extension
arcpy.CheckOutExtension("spatial")

#User inputs
catchmentRaster = arcpy.GetParameterAsText(0)
upDev = arcpy.GetParameterAsText(1)
upForest = arcpy.GetParameterAsText(2)
upAg = arcpy.GetParameterAsText(3)
upWet = arcpy.GetParameterAsText(4)

#User outputs
outTable = arcpy.GetParameterAsText(5)

## ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)

## ---Processes---
#Compute zonal stats
msg("...calculating zonal max of development")
devZStat = arcpy.sa.ZonalStatisticsAsTable(catchmentRaster,"VALUE",upDev,"in_memory/devZStat","DATA","MAXIMUM")
msg("...calculating zonal max of forest")
forZStat = arcpy.sa.ZonalStatisticsAsTable(catchmentRaster,"VALUE",upForest,"in_memory/forZStat","DATA","MAXIMUM")
msg("...calculating zonal max of cultivated")
agrZStat = arcpy.sa.ZonalStatisticsAsTable(catchmentRaster,"VALUE",upAg,"in_memory/agrZStat","DATA","MAXIMUM")
msg("...calculating zonal max of wetland")
wetZStat = arcpy.sa.ZonalStatisticsAsTable(catchmentRaster,"VALUE",upWet,"in_memory/wetZStat","DATA","MAXIMUM")

#Alter field names
msg("...updating field names")
arcpy.AlterField_management(devZStat,"MAX","NLCD2c")
arcpy.AlterField_management(forZStat,"MAX","NLCD4c")
arcpy.AlterField_management(agrZStat,"MAX","NLCD8c")
arcpy.AlterField_management(wetZStat,"MAX","NLCD9c")

#Merge the tables
msg("...joining tables")
arcpy.JoinField_management(devZStat,"VALUE",forZStat,"VALUE","NLCD4c")
arcpy.JoinField_management(devZStat,"VALUE",agrZStat,"VALUE","NLCD8c")
arcpy.JoinField_management(devZStat,"VALUE",wetZStat,"VALUE","NLCD9c")

#Convert from m2 to km2
msg("...converting units to sq km")
arcpy.CalculateField_management(devZStat,"NLCD2c","[NLCD2c] / 1000")
arcpy.CalculateField_management(devZStat,"NLCD4c","[NLCD4c] / 1000")
arcpy.CalculateField_management(devZStat,"NLCD8c","[NLCD8c] / 1000")
arcpy.CalculateField_management(devZStat,"NLCD9c","[NLCD9c] / 1000")

#Save output
arcpy.CopyRows_management(devZStat,outTable)