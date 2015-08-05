# EEP_CalcUpstreamNLCD
#
# Description: Calculates upstream area of grouped land cover types using flow accumulation
#
# Dec 2014, john.fay@duke.edu

import sys, os, arcpy
from arcpy import env
from arcpy.sa import *

env.overwriteOutput = True

#Check out the SA extension
arcpy.CheckOutExtension("spatial")

#User inputs
nlcd = arcpy.GetParameterAsText(0)
fldir = arcpy.GetParameterAsText(1)

#User outputs
upDev = arcpy.GetParameterAsText(2)
upForest = arcpy.GetParameterAsText(3)
upAg = arcpy.GetParameterAsText(4)
upWet = arcpy.GetParameterAsText(5)

#Set environments
env.mask = nlcd
env.extent = nlcd

#Upstream developed
arcpy.AddMessage("Calculating upstream developed") 
dev = Con(nlcd, 1, 0, '"Value" IN (21,22,23,24)')
accDev = FlowAccumulation(fldir,dev,"INTEGER")
accDev.save(upDev)

#Upstream forest
arcpy.AddMessage("Calculating upstream forest") 
forest = Con(nlcd,1,0,'"Value" IN (41,42,43)')
accFor = FlowAccumulation(fldir,forest,"INTEGER")
accFor.save(upForest)

#Upstream ag
arcpy.AddMessage("Calculating upstream agriculture") 
ag = Con(nlcd, 1, 0, '"Value" IN (81,82)')
accAg = FlowAccumulation(fldir,ag,"INTEGER")
accAg.save(upAg)

#Upstream wetland
arcpy.AddMessage("Calculating upstream wetland") 
wtland = Con(nlcd, 1, 0, '"Value" IN (90,95)')
accWet = FlowAccumulation(fldir,wtland,"INTEGER")
accWet.save(upWet)

