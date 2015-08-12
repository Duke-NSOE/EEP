# MAXENT_CalculateUplify.py
#
# Computes the difference in habitat likelihood among current and manaaged scenarios.
#
# Maxent on a projected set of variables is requried to generate this. 
#
# Spring 2015
# John.Fay@duke.edu

import arcpy, sys, os, csv
arcpy.env.overwriteOutput = 1

# Input variables
sppName = arcpy.GetParameterAsText(0)       #Species name, used to find species model results
curFolder = arcpy.GetParameterAsText(1)     #Folder containing maxent output for current conditions
altFolder = arcpy.GetParameterAsText(2)     #Folder containing maxent output for alternate conditions
scenario = altFolder[-2:]                   #Scenario code, last two chars in result folder
respVarTbl = arcpy.GetParameterAsText(3)    #Response variable table listing all the catchments

# Output
upliftCSV = arcpy.GetParameterAsText(4)     #Output table of uplift values for the scenario

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
#---Get the MaxEnt projections files---
#Current conditions file (maxent projection)
curFile = os.path.join(curFolder,"{}_HUC_prj.asc".format(sppName,scenario))
if not os.path.exists(curFile):
    msg("Cannot find current file: {}\nExiting.".format(altFile),"error")
    sys.exit(1)
#Alternate conditions file (maxent projection)
altFile = os.path.join(altFolder,"{}_{}_prj.asc".format(sppName,scenario))
if not os.path.exists(altFile):
    msg("Cannot find projection file: {}\nExiting.".format(altFile),"error")
    sys.exit(1)
msg("ASCII files found. Reading records")

#---Read in the lines of the current projection file---
#Current conditions
f = open(curFile, 'r')
curLines = f.readlines()
f.close()
#Alternate conditions
f = open(altFile, 'r')
altLines = f.readlines()
f.close()

#Initialize the output file and write column headers, named with scenario and "ME" for Maxent
msg("Initializing output CSV")
f = open(upliftCSV,'w')
f.write("GRIDCODE, current_ME, {0}_ME, {0}_uplift_ME\n".format(scenario))

#Loop through catchment records in the response var table
msg("Writing records to output CSV")
recs = arcpy.da.SearchCursor(respVarTbl,"GRIDCODE")
lineIdx = 6     #6 = offset to skip the ASCII header lines
for rec in recs:
    gridCode = rec[0]               #GRIDCODE of catchment
    curProb = curLines[lineIdx]     #value from current projection ASCII
    curVal = float(curProb)         # convert to number
    altLine = altLines[lineIdx]     #value from future projection ASCII
    altVal = float(altLine)         # convert to number
    uplift = altVal - curVal        #Uplift = difference between future and current
    #write the record to the output CSV
    f.write("%s,%2.5f,%2.5f,%2.5f\n" %(gridCode,curVal,altVal,uplift))
    #Increase lineIdx to read next line
    lineIdx += 1

msg("Closing file")
f.close()


