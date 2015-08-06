# MAXENT_CreateProjectionBatchFile.py
#
# Description: Tweaks the RunMe.bat batch file created in the initial run of Maxent
#  so that alternate scenarios can be modeled. 
#
# Inputs include:
#  (1) the initial Runme.bat file
#  (2) a folder containing projection ASCII files
#  (3) a new folder to hold the model outputs
#
#  Model outputs will be sent to the Outputs folder in the MaxEnt directory.
#
# July 2015
# John.Fay@duke.edu

import sys, os, arcpy

# Input variables
origBatchFN = arcpy.GetParameterAsText(0)   # MaxEnt SWD formatted CSV file
prjFolder = arcpy.GetParameterAsText(1)     # Folder containing ASCII projection files
outDir = arcpy.GetParameterAsText(2)        # Folder for maxent outputs

# Output variables
newBatchFN = arcpy.GetParameterAsText(3)   # BAT file to write

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
#Read in the original RunMe.bat file
file = open(origBatchFN,'r')
lineString = file.readline()
file.close()

#Make a dictioary of key/values from data in the line string
lineObjects = lineString.split()

#Create dictionary of modify values
changeDict = {}
changeDict['outputdirectory'] = outDir
changeDict['responsecurves'] = 'false'
changeDict['pictures'] = 'false'
changeDict['jackknife'] = 'false'

#projectionlayers = '.format(prjFolder)

#Initialize the output file
outFile = open(newBatchFN,'w')

#Modify key objects and write to output
for lineObj in lineObjects:
    for key,val in changeDict.items():
        if key in lineObj:
            msg("{}={}".format(key,val))
            outFile.write("{}={} ".format(key,val))
            break
    msg(lineObj)
    outFile.write("{} ".format(lineObj))
msg(' projectionlayers={}'.format(prjFolder))
outFile.write('projectionlayers={}'.format(prjFolder))

outFile.close()

