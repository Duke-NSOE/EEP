# EEP_ExtractESRILandscapeData.py
#
# Description: Calculates zonal stats for various ESRI landscape layers. The layers and how to summarize are
#    included in this script. Others can be added by first creating them and putting them into the Services list

# Import arcpy module
import sys, os, arcpy

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

#User variables
CatchRaster = arcpy.GetParameterAsText(0) #os.path.join(dataWS,"LocalData","Catchments")
outTable = arcpy.GetParameterAsText(1)    #os.path.join(layersDB,"LandscapeStats")

#Set environments
arcpy.env.overwriteOutput = True
arcpy.env.cellSize = CatchRaster

# Get folders
rootWS = os.path.dirname(sys.path[0])
dataWS = os.path.join(rootWS,"Data")

# List of image service layers and the field name to be added
Services = [(r'ESRILayers\ESRI Landscape 4\USA_Soils_Flooding_Frequency.ImageServer','flooding','SUM'),
            (r'ESRILayers\ESRI Landscape 3\Landscape_Modeler\USA_Slope.ImageServer','slope','MEAN'),
            (r'ESRILayers\ESRI Landscape 3\USA_Roads.ImageServer','road_density','MEAN'),
            (r'ESRILayers\ESRI Landscape 2\USA_Soils_Water_Table_Depth.ImageServer','water_table','MEAN'),
            (r'ESRILayers\ESRI Landscape 5\USA_Soils_Erodibility_Factor.ImageServer','erodability','MEAN'),
            (r'ESRILayers\ESRI Landscape 2\USA_Flood_Risk.ImageServer','flood_risk','SUM')]

## REMOVED SERVICES - May 2015
##            (r'ESRILayers\ESRI Landscape 4\USA_Soils_Runoff.ImageServer','runoff','SUM'),
##            (r'ESRILayers\ESRI Landscape 2\USA_Soils_Tfactor.ImageServer','tfactor','MEAN'),
##            (r'ESRILayers\ESRI Landscape 2\USA_Wetlands.ImageServer','wetlands','SUM'),
##            (r'ESRILayers\ESRI Landscape 2\USA_Surface_Water.ImageServer','surface_water','SUM'),         

# Local variables:
ServiceLayer = "LYR"
tmpZStat = "in_memory\\zStat"

# Create the output table
arcpy.AddMessage("Creating output table from catchment raster")
arcpy.CopyRows_management(CatchRaster,outTable)
arcpy.AlterField_management(outTable,"VALUE","COMID","COMID")
arcpy.DeleteField_management(outTable,["COUNT_","SOURCEFC"])

for Service,fld,statType in Services:
    svcName = Service.split("\\")[-1].split(".")[0]
    arcpy.AddMessage("Calculating {} {}".format(statType,svcName))
    
    # Process: Make Image Server Layer
    arcpy.AddMessage("...making service layer")
    svcPath = os.path.join(dataWS,Service)
    arcpy.MakeImageServerLayer_management(svcPath, ServiceLayer, "", "", "NORTH_WEST", "Name", "0", "", "30")

    # Process: Zonal Statistics as Table
    arcpy.AddMessage("...performing zonal stats")
    arcpy.gp.ZonalStatisticsAsTable_sa(CatchRaster, "VALUE", ServiceLayer, tmpZStat, "DATA", statType)

    # Process: Change the field name from generic to something more descriptive
    arcpy.AddMessage("...renaming fields")
    outStatFld = fld+"_"+statType
    arcpy.AlterField_management(tmpZStat,statType,outStatFld)

    # Process: Join Field
    arcpy.AddMessage("...updating output table")
    arcpy.JoinField_management(outTable,"COMID",tmpZStat,"VALUE",[outStatFld])