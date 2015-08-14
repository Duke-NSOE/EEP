# MAXENT_CreateProjectionBatchFiles.py
#
# Description: Tweaks all the RunMe.bat batch files (created in the initial Maxent runs)
#  so that alternate scenarios can be modeled. Tweaks include toggling off jackknifing and
#  response curves, and pointing to different projection and output folders. Also sets
#  autorun to "true" so that Maxent begins instantly.
#
#  The script identifies all the RunMaxent.bat files within the specified base folder and uses
#  it to create a new, modified RunMaxent_.bat file in the same location. The user must then
#  run these batch files (for each species) to calculate uplift. 
#
# July 2015
# John.Fay@duke.edu

import sys, os, arcpy

# Input variables
scenarioPrefix = arcpy.GetParameterAsText(0)
statsRootFolder = arcpy.GetParameterAsText(1)
prjFolder = arcpy.GetParameterAsText(2)


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
#Find all the runme.bat files in the statsRootFolder
fileLocs = []
for r,d,f in os.walk(statsRootFolder):
    if "RunMaxent.bat" in f:
        fileLocs.append(r)

#Loop through each RunMaxent.bat file location
for fileLoc in fileLocs:
    #Set the in and out names
    origBatchFN = os.path.join(fileLoc,"RunMaxent.bat")
    newBatchFN = os.path.join(fileLoc,"RunMaxent_{}.bat".format(scenarioPrefix))
    msg("...Creating {}".format(newBatchFN))

    #Set and create the output dir
    outDir = os.path.join(fileLoc,"Output_{}".format(scenarioPrefix))
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    arcpy.SetParameterAsText(3,outDir)

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

    #Initialize the output file
    outFile = open(newBatchFN,'w')

    #Modify key objects and write to output
    for lineObj in lineObjects:
        lineString = lineObj
        for key,val in changeDict.items():
            if key in lineString:
                lineString = "{}={} ".format(key,val)
                break
        outFile.write("{} ".format(lineString))
    #Add pointer to projection folder
    outFile.write('projectionlayers={}'.format(prjFolder))
    #Set to autorrun
    outFile.write(' autorun=true')
    outFile.write(' threads=4')
    outFile.write(' askoverwrite=false')

    outFile.close()

