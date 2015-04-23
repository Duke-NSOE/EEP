#AccumNLCD.py
#
# Description: Calculates upstream area of grouped land cover types using flow accumulation

import sys, os, arcpy
from arcpy import env
from arcpy.sa import *

env.overwriteOutput = True

#Check out the SA extension
arcpy.CheckOutExtension("spatial")

#User inputs
catchments = arcpy.GetParameterAsText(0)
NHDfac = arcpy.GetParameterAsText(1)
upDev = arcpy.GetParameterAsText(2)
upForest = arcpy.GetParameterAsText(3)
upAg = arcpy.GetParameterAsText(4)
upWet = arcpy.GetParameterAsText(5)

#User outputs
NLCDstats = arcpy.GetParameterAsText(6)

#Local variables
NLCDtable = "in_memory/cumNLCD"

#ZonalStats
arcpy.AddMessage("Creating output table")
ZonalStatisticsAsTable(catchments,"VALUE",NHDfac,NLCDtable,"NODATA","MAXIMUM")
arcpy.AlterField_management(NLCDtable,"VALUE","COMID")
arcpy.AlterField_management(NLCDtable,"MAX","CumArea")
arcpy.DeleteField_management(NLCDtable,["COUNT","AREA"])

arcpy.AddMessage("...Calculating upstream developed")
ZonalStatisticsAsTable(catchments,"VALUE",upDev,"in_memory/cumDev","NODATA","MAXIMUM")
arcpy.AlterField_management("in_memory/cumDev","MAX","AccDev")
arcpy.JoinField_management(NLCDtable,"COMID","in_memory/cumDev","VALUE",["AccDev"])

arcpy.AddMessage("...Calculating upstream forest")
ZonalStatisticsAsTable(catchments,"VALUE",upForest,"in_memory/cumFor","NODATA","MAXIMUM")
arcpy.AlterField_management("in_memory/cumFor","MAX","AccFor")
arcpy.JoinField_management(NLCDtable,"COMID","in_memory/cumFor","VALUE",["AccFor"])

arcpy.AddMessage("...Calculating upstream cropland")
ZonalStatisticsAsTable(catchments,"VALUE",upAg,"in_memory/cumAg","NODATA","MAXIMUM")
arcpy.AlterField_management("in_memory/cumAg","MAX","AccAg")
arcpy.JoinField_management(NLCDtable,"COMID","in_memory/cumAg","VALUE",["AccAg"])

arcpy.AddMessage("...Calculating upstream wetland")
ZonalStatisticsAsTable(catchments,"VALUE",upWet,"in_memory/cumWet","NODATA","MAXIMUM")
arcpy.AlterField_management("in_memory/cumWet","MAX","AccWet")
arcpy.JoinField_management(NLCDtable,"COMID","in_memory/cumWet","VALUE",["AccWet"])

arcpy.AddMessage("...Converting areas to percentages ")
arcpy.AddField_management(NLCDtable,"pctDev","FLOAT",5,2)
arcpy.AddField_management(NLCDtable,"pctFor","FLOAT",5,2)
arcpy.AddField_management(NLCDtable,"pctAg","FLOAT",5,2)
arcpy.AddField_management(NLCDtable,"pctWet","FLOAT",5,2)


NLCDselection = arcpy.MakeTableView_management(NLCDtable,"SelRows","CumArea > 0")
arcpy.CalculateField_management(NLCDselection,"pctFor","([AccFor] / [CumArea]) * 100")
arcpy.CalculateField_management(NLCDselection,"pctDev","[AccDev] / [CumArea] * 100")
arcpy.CalculateField_management(NLCDselection,"pctWet","[AccWet] / [CumArea] * 100")
arcpy.CalculateField_management(NLCDselection,"pctAg","[AccAg] / [CumArea] * 100")

arcpy.AddMessage("...Cleaning up")
arcpy.CopyRows_management("SelRows",NLCDstats)