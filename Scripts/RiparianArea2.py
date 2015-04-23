#RiparianArea.py
#
# Description: Creates a binary raster of riparian areas which is defined
#  as all pixels within X meters above the stream cell into which it flows. 

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
tempWS = os.path.join(rootWS,"Scratch","FlowlineScratch")
env.workspace = dataWS
env.scratchWorkspace = tempWS
env.snapRaster = "elev_cm"


#Create the kernels
nbrE = NbrIrregular(os.path.join(rootWS,"Scripts","Kernels","1.txt"))
nbrSE = NbrIrregular(os.path.join(rootWS,"Scripts","Kernels","2.txt"))
nbrS = NbrIrregular(os.path.join(rootWS,"Scripts","Kernels","4.txt"))
nbrSW = NbrIrregular(os.path.join(rootWS,"Scripts","Kernels","8.txt"))
nbrW = NbrIrregular(os.path.join(rootWS,"Scripts","Kernels","16.txt"))
nbrNW = NbrIrregular(os.path.join(rootWS,"Scripts","Kernels","32.txt"))
nbrN = NbrIrregular(os.path.join(rootWS,"Scripts","Kernels","64.txt"))
nbrNE = NbrIrregular(os.path.join(rootWS,"Scripts","Kernels","128.txt"))

#Get the input rasters
elev_cm = "elev_cm"

#Create the elev offset rasters
elevE = FocalStatistics(elev_cm,nbrE,"MAXIMUM")
elevSE = FocalStatistics(elev_cm,nbrSE,"MAXIMUM")
elevS = FocalStatistics(elev_cm,nbrS,"MAXIMUM")
elevSW = FocalStatistics(elev_cm,nbrSW,"MAXIMUM")
elevW = FocalStatistics(elev_cm,nbrW,"MAXIMUM")
elevNW = FocalStatistics(elev_cm,nbrNW,"MAXIMUM")
elevN = FocalStatistics(elev_cm,nbrN,"MAXIMUM")
elevNE = FocalStatistics(elev_cm,nbrNE,"MAXIMUM")

#Get the flowdir raster
fdrX = Int(Log2("flowdir") + 1)

#Create elevation of downstream cell
elevX = Pick(fdrX,[elevE,elevSE,elevS,elevSW,elevW,elevNW,elevN,elevNE])

#Subtract current elev from elev of downstream cell
elevDrop = elev_cm - elevX

#elevDrop.save("ElevDrop")

accumDrop = FlowLength("fdrnull","DOWNSTREAM",elevDrop)
