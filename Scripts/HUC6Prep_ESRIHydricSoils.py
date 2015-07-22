# HUC6Prep_ESRIHydricSoils.py
#
# Description: Computes the amount of Hydric soils within each catchment

# Import arcpy module
import sys, os, arcpy

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

#User variables
CatchRaster = arcpy.GetParameterAsText(0)#r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\cat'
NLCDRaster = arcpy.GetParameterAsText(0)#r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\nlcd_2011'
outTable = arcpy.GetParameterAsText(0)#r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\foo'

#Set environments
arcpy.env.overwriteOutput = True
arcpy.env.cellSize = CatchRaster

# Get paths
rootWS = os.path.dirname(sys.path[0])
dataWS = os.path.join(rootWS,"Data")

# Local variables:
Service = r'ESRILayers\ESRI Landscape 4\USA_Soils_Hydric_Classification.ImageServer'
ServiceLayer = "LYR"
tmpZStat = "in_memory\\zStat"

# ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        msg(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)
        

## PROCESSES 
# Process: Make Image Server Layer
svcName = Service.split("\\")[-1].split(".")[0]
msg("Linking to {} on ESRIs Server...".format(svcName))

msg("...extracting data. (This takes a while)")
svcPath = os.path.join(dataWS,Service)
arcpy.MakeImageServerLayer_management(svcPath, ServiceLayer, "", "", "NORTH_WEST", "Name", "0", "", "30")

# Extract Hydric Soils from Layer, excluding areas coincident with NLCD urban classes
msg("Excluding urban areas")
hydricRaster = arcpy.sa.Con(NLCDRaster,ServiceLayer,"","VALUE >= 30")

# Convert to a binary hydric/non-hydric layer (2="All hydric"; 4="Partially hydric")
msg("Converting soils raster to binary hydric/non-hydric raster")
hydricBinary = arcpy.sa.Con(hydricRaster,1,0,"Value in (2, 4)")

# Computing the proportion of hydric soils within each catchment
msg("Computing percent catchment area classified as hydric")
arcpy.gp.ZonalStatisticsAsTable_sa(CatchRaster, "VALUE", hydricBinary, tmpZStat, "DATA","MEAN")

# Process: Change the field name from generic to something more descriptive
msg("...renaming fields")
outStatFld = "PCT_HYDRIC"
arcpy.AlterField_management(tmpZStat,"MEAN",outStatFld)

# Add the area_hydric field and compute its values (0.09 converts cells to km2)
msg("Computing area from percentages")
arcpy.AddField_management(tmpZStat,"AREA_HYDRIC","DOUBLE",10,3)
arcpy.CalculateField_management(tmpZStat,"AREA_HYDRIC","[PCT_HYDRIC] * [AREA]")

# Create the output table
msg("Creating output table from catchment raster")
arcpy.CopyRows_management(CatchRaster,outTable)
arcpy.AlterField_management(outTable,"VALUE","COMID","COMID")
arcpy.DeleteField_management(outTable,["COUNT_","SOURCEFC"])

# Process: Join Field
msg("...updating output table")
arcpy.JoinField_management(outTable,"COMID",tmpZStat,"VALUE",["PCT_HYDRIC","AREA_HYDRIC"])