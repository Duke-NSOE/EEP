#----------------------------------------------------------------------------------------
#PrepData.py
#
# Description: Extracts data for a user provided NHD HUC6 for stream habitat assessment
#
# Dec 2014
# John.Fay@duke.edu
#----------------------------------------------------------------------------------------

import sys, os, arcpy

#Misc functions
def msg(str,severity=""):
    print str
    if severity == "warning": arcpy.AddWarning(str)
    elif severity == "error": arcpy.AddError(str)
    else: arcpy.AddMessage(str)
    return

#FolderNames: These must exist prior to script execution
rootDir = os.path.dirname(sys.path[0])
dataDir = os.path.join(rootDir,"Data")
tempDir = os.path.join(rootDir,"Scratch")
gridDir = os.path.join(dataDir,"LocalData")
projGDB = os.path.join(dataDir,"SiteLayers.gdb")
nhdSDE = os.path.join(dataDir,"SDE_connections","NHDpplusV2.sde")
usaSDE = os.path.join(dataDir,"SDE_connections","USA.sde")


#DEBUG
debug = 1
if debug:
    sys.argv.append('030201')
    sys.argv.append(os.path.join(projGDB,"HUC6"))
    sys.argv.append(os.path.join(projGDB,"HUC12"))
    sys.argv.append(os.path.join(projGDB,"MaskPoly"))
    sys.argv.append(os.path.join(projGDB,"CatchmentsPoly"))
    sys.argv.append(os.path.join(projGDB,"Flowlines"))
    sys.argv.append(os.path.join(projGDB,"FlowlineMidpoints"))
    sys.argv.append(os.path.join(gridDir,"Mask"))
    sys.argv.append(os.path.join(gridDir,"NHDCatchments"))
    sys.argv.append(os.path.join(gridDir,"FlowDir"))
    sys.argv.append(os.path.join(gridDir,"FdrNull"))
    sys.argv.append(os.path.join(gridDir,"Elev_cm"))
    sys.argv.append(os.path.join(gridDir,"NLCD2011"))
    sys.argv.append(os.path.join(gridDir,"Canopy"))
    sys.argv.append(os.path.join(gridDir,"Imperv"))

#USER INPUTS/OUTPUTS
x = 1                                   #sys.argv counter
## HUC6 ID Input
HUC6 = sys.argv[x]; x+=1
## Vector outputs
HUC6_poly = sys.argv[x]; x+=1           #HUC12 Polygons in selected HUC6
HUC12_poly = sys.argv[x]; x+=1          #Selecte HUC6 Polygons
MaskPoly = sys.argv[x]; x+=1            #Mask Polygon (Dissolved Catchments)
CatchPoly = sys.argv[x]; x+=1           #Catchment polygons
Flowlines = sys.argv[x]; x+=1           #Flowlines in selected HUC6
FlowlineMidPoints = sys.argv[x]; x+=1   #Flowline midpoints
## Raster outputs
MaskGrid = sys.argv[x]; x+=1            #Raster mask
Catchments = sys.argv[x]; x+=1          #Catchment raster
FlowDir = sys.argv[x]; x+=1             #NHD Flow Direction
FdrNull = sys.argv[x]; x+=1             #NHD FlowDirNull       
Elev_cm = sys.argv[x]; x+=1             #NHD Elevatiom (cm)                   
NLCD2011 = sys.argv[x]; x+=1            #NLCD Land Cover 
Canopy = sys.argv[x]; x+=1              #NLCD Canopy Cover
Imperv = sys.argv[x]; x+=1              #NLCD Impervious Surface

#LOCAL VARIABLES
nhdWBD = os.path.join(nhdSDE,"NHDplusV2.SDE.WBDHU6")
wdbSubWatershed = os.path.join(nhdSDE,"NHDplusV2.SDE.WBD_Subwatershed")

#NHD Image Layers
nhdURL = "http://ns-a224-jpfay.win.duke.edu:6080/arcgis/services/NHDplusV2/"
catLyr = arcpy.MakeImageServerLayer_management(nhdURL+"cat/ImageServer","catLyr")
elevLyr = arcpy.MakeImageServerLayer_management(nhdURL+"elev_cm/ImageServer","elevLyr")
fdrLyr = arcpy.MakeImageServerLayer_management(nhdURL+"fdr/ImageServer","fdrLyr")
fdrnullLyr = arcpy.MakeImageServerLayer_management(nhdURL+"cat/ImageServer","fdrnullLyr")

#NHD Catchment query
def getLayer(LayerID,OutName,where=''):
    ## See http://blogs.esri.com/esri/arcgis/2013/10/10/quick-tips-consuming-feature-services-with-geoprocessing/
    baseURL = "http://ns-a224-jpfay.win.duke.edu:6080/arcgis/rest/services/NHDplusV2/NHD2Features/FeatureServer/{}/query".format(LayerID)
    query = "?where={}&outFields=*&returnGeometry=true&f=json&token=".format(where, fields, token)
    fsURL = baseURL + query
    fs = arcpy.FeatureSet()
    fs.load(fsURL)
    arcpy.CopyFeatures_management(fs,OutName)
    return 

getLayer(2,HUC6_poly,"HUC6='{}'".format(HUC6))                  #HUC6 boundaries
getLayer(3,Flowlines,"REACHCODE LIKE '{}%'".format(HUC6))       #Flowlines