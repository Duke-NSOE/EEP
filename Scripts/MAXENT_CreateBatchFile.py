# MAXENT_CreateBatchFile.py
#
# Creates a batch file (.bat) used to run MaxEnt with the supplied files. The way
#  this script is configured, the workspace must contain a MaxEnt folder (containing
#  the MaxEnt.jar file) in the project's root folder. 
#
# Inputs include:
#  (1) the MaxEnt samples with data format (SWD) CSV file, 
#  (2) a list of field names to exclude by default in the analysis
#  (3) a list of fields that should be set to categorical
#  (4) a folder containing projection ASCII files
#
#  Model outputs will be sent to the Outputs folder in the MaxEnt directory.
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy

# Input variables
swdFile = arcpy.GetParameterAsText(0)           # MaxEnt SWD formatted CSV file
excludeFlds = arcpy.GetParameterAsText(1)       # Fields to toggle off by default
categoricalFlds = arcpy.GetParameterAsText(2)   # Fields to set as categorical (not continuous)
prjFolder = arcpy.GetParameterAsText(3)         # Folder containing ASCII projection files (optional)
runMaxent = arcpy.GetParameterAsText(4)         # Boolean whether to run MaxEnt when finished

# Output variables
maxentFile = arcpy.GetParameterAsText(5)        # BAT file to write

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
# Check that the Maxent folder exists and that the maxent.jar file is in it
maxentPath = os.path.abspath(sys.path[0]+ "\\..\\Maxent")
if not(os.path.exists(maxentPath)):
    msg("Maxent folder cannot be found","error")
    sys.exit(0)
elif not(os.path.exists(maxentPath+"\\maxent.jar")):
    msg("Maxent.jar file cannot be found in {}./n Exiting.".format(maxentPath),"error")
    sys.exit(0)
else:
    msg("Maxent folder set to {}".format(maxentPath))

# Check that the output folder exists; create it if not
outDir = os.path.abspath(os.path.dirname(swdFile)+"\\Output")
if not(os.path.exists(outDir)):
    msg("Creating output directory")
    os.mkdir(outDir)
else: msg("Setting output to {}".format(outDir))

# Begin creating the batch run string with boilerplate stuff
msg("Initializing the Maxent batch command")
runString = "java -mx2048m -jar {}".format(os.path.join(maxentPath,"maxent.jar"))

# set samples file
msg("Setting samples file to {}".format(swdFile))
runString += " samplesfile={}".format(swdFile)

# set enviroment layers file
msg("Setting enviroment layers file to {}".format(swdFile))
runString += " environmentallayers={}".format(swdFile)
    
# set output directory
msg("Setting output directory to {}".format(outDir))
runString += " outputdirectory={}".format(outDir)

# enable response curves
msg("Enabling response curves")
runString += " responsecurves=true"

# enable jackknifing
msg("Enabling jackknifing")
runString += " jackknife=true"

# disable pictures
msg("Disabling drawing pictures")
runString += " pictures=false"

# turn off background spp
msg('Toggling "background" species')
runString += " togglespeciesselected=background"

# toggle off all species in excludeFields
## Create list from excludeFields input
excludeItems = excludeFlds.split(";")
## Remove species, X, and Y columns from list, if included
if ("Species") in excludeItems: excludeItems.remove("Species")
if ("X") in excludeItems: excludeItems.remove("X")
if ("Y") in excludeItems: excludeItems.remove("Y")

## Loop through list; if header item not in include list, toggle it off
for excludeItem in excludeItems: 
    msg("...disabling {} field".format(excludeItem))
    runString += " togglelayerselected={}".format(excludeItem)
            
# Set categorical fields
if categoricalFlds:
    ## Split the list string in to list items
    catItems = categoricalFlds.split(";")
    ## Loop through each item in the list and set it to categorical
    for catItem in catItems:
        msg("Setting {} field to categorical".format(catItem))
        runString += " togglelayertype={}".format(catItem)

# Set the projection file directory and turn on projections, if supplied
if prjFolder:
    msg("Setting projection folder to {}".format(prjFolder))
    runString += " projectionlayers={}".format(prjFolder)

# Write commands to batch file
msg("Writing commands to batchfile {}".format(maxentFile))
outFile = open(maxentFile,'w')
outFile.write(runString)
outFile.close()

# Run MaxEnt, if opted
if runMaxent == 'true':
    msg("Opening MaxEnt")
    import subprocess
    #subprocess.call(maxentFile)
    subprocess.Popen(maxentFile)

    
