# UPLIFT_WetlandExpansion.py
#
# Description: Computes the amount of Hydric soils within each catchment

# Import arcpy module
import sys, os, arcpy

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

#User variables
NLCDRaster = r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\nlcd_2011'
outRaster =  r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\wetlanduplift'

#Set environments
arcpy.env.overwriteOutput = True
arcpy.env.cellSize = NLCDRaster

# Get paths
rootWS = os.path.dirname(sys.path[0])
dataWS = os.path.join(rootWS,"Data")

# Local variables:
Service = r'ESRILayers\ESRI Landscape 4\USA_Soils_Hydric_Classification.ImageServer'
HydricSoilsLayer = "LYR"

# ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)

## PROCESSES 
# Process: Make Image Server Layer of the Hydric Soils
svcName = Service.split("\\")[-1].split(".")[0]
msg("...linking to {} on ESRIs Server...".format(svcName))

# Process: Extract data from ESRI server
svcPath = os.path.join(dataWS,Service)
arcpy.MakeImageServerLayer_management(svcPath, HydricSoilsLayer, "", "", "NORTH_WEST", "Name", "0", "", "30")

# Setting the extent
msg("...setting the extent to the NLCD raster")
arcpy.env.extent = NLCDRaster

# Create a level1 NLCD raster
msg("...creating level 1 NLCD raster")
#NLCD1 = arcpy.sa.Int(arcpy.Raster(NLCDRaster) / 10)

# Set hydric soils to wetland, otherwise keep NLCD (Level 1) values
msg("...converting all areas with hydric soils as wetlands")
hydricNLCD = arcpy.sa.Con(HydricSoilsLayer,90,NLCDRaster,"Value in (2, 4)")

# Creates a raster where urban areas are zero, otherwise hydric values
msg("...reverting wetlands on developed areas back to developed")
#Keep urban, set all other areas to hydric
hydricRaster = arcpy.sa.Con(NLCDRaster,NLCDRaster,hydricNLCD,"VALUE IN (21, 22, 23, 24)")

# Save the output
msg("...saving output")
hydricRaster.save(outRaster)