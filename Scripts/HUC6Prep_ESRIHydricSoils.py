# HUC6Prep_ESRIHydricSoils.py
#
# Description: Computes the amount of Hydric soils within each catchment

# Import arcpy module
import sys, os, arcpy

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

#User variables
#CatchRaster = arcpy.GetParameterAsText(0) #os.path.join(dataWS,"LocalData","Catchments")
#outTable = arcpy.GetParameterAsText(1)    #os.path.join(layersDB,"LandscapeStats")
CatchRaster = r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\cat'
NLCDRaster = r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\nlcd_2011'
outTable = r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\foo'

#Set environments
arcpy.env.overwriteOutput = True
arcpy.env.cellSize = CatchRaster

# Get folders
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
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)
svcName = Service.split("\\")[-1].split(".")[0]
msg("Extracting {}".format(svcName))

## PROCESSES 
# Process: Make Image Server Layer
msg("...making service layer")
svcPath = os.path.join(dataWS,Service)
arcpy.MakeImageServerLayer_management(svcPath, ServiceLayer, "", "", "NORTH_WEST", "Name", "0", "", "30")

# Extract Hydric Soils from Layer, excluding areas coincident with NLCD urban classes
msg("Extracting soils data not falling within urban areas")
hydricRaster = arcpy.sa.Con(NLCDRaster,ServiceLayer,"","VALUE >= 30")

# Convert to a binary hydric/non-hydric layer
msg("Converting soils raster to binary hydric/non-hydric raster")
hydricBinary = arcpy.sa.Con(hydricRaster,1,0,"Value in (2, 4)")

# Computing the proportion of hydric soils within each catchment
arcpy.gp.ZonalStatisticsAsTable_sa(CatchRaster, "VALUE", hydricBinary, tmpZStat, "DATA","MEAN")

# Process: Change the field name from generic to something more descriptive
arcpy.AddMessage("...renaming fields")
outStatFld = "PCT_HYDRIC"
arcpy.AlterField_management(tmpZStat,statType,outStatFld)

# Create the output table
arcpy.AddMessage("Creating output table from catchment raster")
arcpy.CopyRows_management(CatchRaster,outTable)
arcpy.AlterField_management(outTable,"VALUE","COMID","COMID")
arcpy.DeleteField_management(outTable,["COUNT_","SOURCEFC"])

# Process: Join Field
arcpy.AddMessage("...updating output table")
arcpy.JoinField_management(outTable,"COMID",tmpZStat,"VALUE",[outStatFld])