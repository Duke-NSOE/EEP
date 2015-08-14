# UPLIFT_ResponseVarsToProjections.py
#
# Converts a table of response variables into a series of ASCII
#   "pseudo rasters" - one for each environment layer in the SWD file. Each
#   raster is one column wide and several rows long, with each row corresponding
#   to a single NHD catchment. These ASCII pseudo rasters enable MaxEnt to "project"
#   model results into a new ASCII file, one that lists the habitat likelihood for
#   each "pixel", which is actually an NHD catchment.
#
# August 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv
arcpy.env.overwriteOutput = True

# Input variables
respvarTbl = arcpy.GetParameterAsText(0)
prjFolder = arcpy.GetParameterAsText(1)

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
#Check that the output folder exists; ask to create if not
if not(os.path.exists(prjFolder)):
    msg("Creating output folder: {}".format(prjFolder))
    os.mkdir(prjFolder)
else:
    msg("Using existing projection output folder...")

#Create the ASCII header
msg("Creating the header lines for the output pseudo ASCII files")
##Get the number of lines in the file to determine how many rows to set in the ASCII header
rowCount = arcpy.GetCount_management(respvarTbl).getOutput(0)
##Create the header string, incorporating the number of rows determined above
asciiHeader = 'ncols\t1\nnrows\t{0}\nxllcorner\t0\nxyllcorner\t0\ncellsize\t1\nNODATA_value\t-9999\n'.format(rowCount)

#Get a list if fields
fldList = []
for f in arcpy.ListFields(respvarTbl):
    if f.type in ("Double","Float","Integer","Single","SmallInteger"):
        fldList.append(f.name)
envVarsCount = len(fldList)

#Start creating the files
msg("{} ASCII layers will be created".format(envVarsCount))

##loop through each environmetal variable 
for fld in fldList:
    msg("...Processing variable {}".format(fld))
    ##Create the output file
    outFN = os.path.join(prjFolder,fld + ".asc")
    file = open(outFN,'w')
    ##Write the ASCII header lines
    file.write(asciiHeader)
    ##Read the CSV lines and write out the selected column
    records = arcpy.da.SearchCursor(respvarTbl,fld)
    for rec in records:
        outVal = rec[0]
        if outVal is None: outVal = -9999
        file.write("{}\n".format(outVal))
    ##Close the file
    file.close()

msg("ASCII projection creation complete!")


