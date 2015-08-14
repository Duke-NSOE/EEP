# MAXENT_RunBatches.py
#
# Description: Iterates through species folders in Habitat Stats folders and
#  runs maxent batches sequentially.
#
# Inputs:
#    The master list of variables (ResponseVars.xlsx in Data Folder)
#    Folder containing Variable Importance CSVs for the modeled species.
#
# Output is a single CSV listing each value and the averages of:
#  - Percent contribution               (spp_PC)
#  - Permeability importance            (spp_PI)
#  - Model gain without the variable    (spp_WOut)
#  - Model gain with only the variable  (spp_Only)
#
# July 2015
# John.Fay@duke.edu

import arcpy, sys, os
arcpy.env.overwriteOutput = 1

# Input variables
batchName = arcpy.GetParameterAsText(0)   #"RunMaxent.bat"
statsFolder = arcpy.GetParameterAsText(1) #r'C:\WorkSpace\EEP_Tool\TarPamStats'


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
# Walk through folders and find bat files
for r,d,f in os.walk(statsFolder):
    if batchName in f:
        runCmd =  os.path.join(r,batchName)
        os.system(runCmd)