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
sppName = arcpy.GetParameterAsText(0)
currentFolder = arcpy.GetParameterAsText(1)
resultFolder = arcpy.GetParameterAsText(2)
scenario = resultFolder[-2:]
respVarTbl = arcpy.GetParameterAsText(3)

##sppName = "Nocomis_leptocephalus"
##currentFolder = r"C:\WorkSpace\EEP_Tool\HabitatStats\Nocomis_leptocephalus\Output_HUC"
##resultFolder = r"C:\WorkSpace\EEP_Tool\HabitatStats\Nocomis_leptocephalus\Output_BU"
##scenario = resultFolder[-2:]
##respVarTbl = r"C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\ResponseVars"

# Output
upliftCSV = arcpy.GetParameterAsText(4)

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
#-- Get the MaxEnt projections files---
#Current conditions file
curFile = os.path.join(currentFolder,"{}_HUC_prj.asc".format(sppName,scenario))
if not os.path.exists(curFile):
    msg("Cannot find current file: {}\nExiting.".format(ascFile),"error")
    sys.exit(1)
#Future conditions file
ascFile = os.path.join(resultFolder,"{}_{}_prj.asc".format(sppName,scenario))
if not os.path.exists(ascFile):
    msg("Cannot find projection file: {}\nExiting.".format(ascFile),"error")
    sys.exit(1)
msg("ASCII files found. Reading records")

#--Get the lines of the current projection file (likelihood under current conditions)
f = open(curFile, 'r')
curLines = f.readlines()
f.close()
curRecords = len(curLines)
msg("  {} current records extracted".format(curRecords - 6))

#--Get the lines of the  future projection file (likelihood under alternate scenarios)
f = open(ascFile, 'r')
prjLines = f.readlines()
f.close()
prjRecords = len(prjLines)
msg("  {} future records extracted".format(prjRecords - 6))

#Initialize the output file
msg("Initializing output CSV")
f = open(upliftCSV,'w')
f.write("GRIDCODE, {0}_current, {0}_alternate, {0}_uplift\n".format(scenario))

#Loop through catchment records in the response var table
msg("Writing records to output CSV")
recs = arcpy.da.SearchCursor(respVarTbl,"GRIDCODE")
lineIdx = 6     #6 = offset to skip the ASCII header lines
for rec in recs:
    gridCode = rec[0]               #GRIDCODE of catchment
    curProb = curLines[lineIdx]     #value from current projection ASCII
    curVal = float(curProb)         # convert to number
    prjLine = prjLines[lineIdx]     #value from future projection ASCII
    prjVal = float(prjLine)         # convert to number
    uplift = prjVal - curVal        # Uplift=difference between future and current
    #write the record to the output CSV
    f.write("%s,%2.5f,%2.5f,%2.5f\n" %(gridCode,curVal,prjVal,uplift))
    #Increase lineIdx to read next line
    lineIdx += 1

msg("Closing file")
f.close()


