#FlowlineStats.py

import sys, os, arcpy
from arcpy import env
from arcpy.sa import *

env.overwriteOutput = True

#Check out the SA extension
arcpy.CheckOutExtension("spatial")

#Set the workspaces
rootWS = os.path.dirname(sys.path[0])
dataWS = os.path.join(rootWS,"Data","Localdata")
nhdWS = os.path.join(rootWS,"Data","NHDplusV2 on NS-GIS as user.sde")
tempWS = os.path.join(rootWS,"Scratch")
env.workspace = dataWS
env.scratchWorkspace = tempWS

#Get Inputs
catRaster = os.path.join(dataWS,"catchments")
nlcdRaster = os.path.join(dataWS,"NLCD2011.img")
fdrNull = os.path.join(dataWS,"fdrnull")

#Process: Create flow line mask
flowMask  = Con(IsNull(fdrNull),1)

#Set the mask environment
arcpy.env.mask = flowMask

#Process: Reduce NLCD to buffer classes
buffOnly = Con(nlcdRaster,1,"",'"VALUE" IN (41,42,43,90,95)')

#Process: Create stream line patches
buffZone = RegionGroup(buffOnly,"EIGHT")
buffZoneCount = Lookup(buffZone,"COUNT")

#Process: Convert buffZone to line

#Process: Zonal stats on buffZones in catchments
zstat = ZonalStatisticsAsTable(catRaster,"VALUE",buffZoneCount,"in_memory\FlowLineX")
#Variety = fragments
#Count = proxy for 