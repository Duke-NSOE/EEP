# MAXENT_SWDtoProjectionASCIIs.py
#
# Converts a MaxEnt samples with data (SWD) CSV file into a series of ASCII
#   "pseudo rasters" - one for each environment layer in the SWD file. Each
#   raster is one column wide and several rows long, with each row corresponding
#   to a single NHD catchment. These ASCII pseudo rasters enable MaxEnt to "project"
#   model results into a new ASCII file, one that lists the habitat likelihood for
#   each "pixel", which is actually an NHD catchment.
#
# The input SWD CSV file should include rows for both species occurrence and background
#   samples. The first column should list whether the row is a species occurrence or
#   background. The second and third column should have values representing X and Y
#   coordinates, though these values need not actually mean anything. And the remaining
#   columns should include all the environment layer values for the sample/background pts.
#
# The model outputs a folder containing all the ASCII files - one for each env layer. 
# 
# Spring 2015
# John.Fay@duke.edu

import arcpy, sys, os

# Script variables
swdFilename = arcpy.GetParameterAsText(0)   #MaxEnt samples with data CSV file
prjFolder = arcpy.GetParameterAsText(1)    #Folder that will contain all the pseudo ASCII files

# ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)

# ---Processes---
#Get and open the CSV file; put data into the lines list
msg("Reading the values from the MaxEnt samples with data (SWD) csv file")        
file = open(swdFilename,'r')
lines = file.readlines()
file.close()

#Check that the output folder exists; ask to create if not
if not(os.path.exists(prjFolder)):
    msg("Creating output folder: {}".format(prjFolder))
    os.mkdir(prjFolder)
else:
    msg("Using existing projection output folder...")

#Create the ASCII header
msg("Creating the header lines for the output pseudo ASCII files")
##Get the number of lines in the file to determine how many rows to set in the ASCII header
rowCount = len(lines) - 1
##Create the header string, incorporating the number of rows determined above
asciiHeader = 'ncols\t1\nnrows\t{0}\nxllcorner\t0\nxyllcorner\t0\ncellsize\t1\nNODATA_value\t-9999\n'.format(rowCount)

#Create output files for each environment layer in the SWD file
msg("Creating output ASCII files...")
##Get the header line of the CSV file (the first object in the lines list)
headerLine = lines[0]

##Split the items in the string into the a list called "envVars"
envVars = headerLine.split(",")

##Count the number of env vars and report to user
envVarsCount = len(envVars)
msg("{} ASCII layers will be created".format(envVarsCount))

##loop through each environmetal variable 
for colIdx in range(1,envVarsCount):
    msg("...Processing layer{}: {}".format(colIdx, envVars[colIdx]))
    ##Create the output file
    if colIdx < len(envVars) - 1: #Need to remove the new line char from the last item
        outFN = os.path.join(prjFolder,envVars[colIdx] + ".asc")
    else:
        outFN = os.path.join(prjFolder,envVars[colIdx][:-1] + ".asc")
    file = open(outFN,'w')
    ##Write the ASCII header lines
    file.write(asciiHeader)
    ##Read the CSV lines and write out the selected column
    for line in lines[1:]:
        if colIdx < len(envVars) - 1:
            outValue = line.split(",")[colIdx]
        else:
            outValue = line.split(",")[colIdx][:-1]
        file.write(outValue + "\n")
    ##Close the file
    file.close()

msg("ASCII projection creation complete!")


