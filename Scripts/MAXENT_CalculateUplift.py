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
sppName = "Nocomis_leptocephalus"
resultFolder = r"C:\WorkSpace\EEP_Tool\HabitatStats\Nocomis_leptocephalus\Output_BU"
scenario = resultFolder[-2:]

# Output
upliftCSV = r"C:\WorkSpace\EEP_Tool\HabitatStats\Nocomis_leptocephalus_ME_BU.csv"

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
#-- Get the MaxEnt result files---
#ASCII projection file
ascFile = os.path.join(resultFolder,"{}_{}_prj.asc".format(sppName,scenario))
if not os.path.exists(ascFile):
    msg("Cannot find projection file: {}\nExiting.".format(ascFile),"error")
    sys.exit(1)
#Current prediction file
sppFile = os.path.join(resultFolder,sppName + ".csv")
if not os.path.exists(sppFile):
    msg("Cannot find prediction file: {}\nExiting.".format(sppFile),"error")
    sys.exit(1)

#Get the lines of the prediction file (likelihood under current conditions)
f = open(sppFile,'r')
sppLines = f.readlines()
f.close()
sppRecords = len(sppLines)

#Get the lines of the projection file (likelihood under alternate scenarios)
f = open(ascFile, 'r')
prjLines = f.readlines()
f.close()
prjRecords = len(prjLines)

#Initialize the output file
f = open(upliftCSV,'w')
f.write("GRIDCODE, {0}_current, {0}_alternate, {0}_uplift\n".format(scenario))

#Loop through the records and write the output
msg("Writing {} values to output file".format(sppRecords))
for lineIdx in range(1,sppRecords):
    sppLine = sppLines[lineIdx][:-1] #[:-1] is to skip newline char at end
    prjLine = prjLines[lineIdx + 5][:-1]  #Skip ASCII header (6 lines); [:-1] is to skip newline char at end
    #Get values from the spp line
    sppLineData = sppLine[:-1].split(",")
    gridCode = sppLineData[0][:-2] #First column is the catchment GRIDCODE; lop off decimal
    curProb = float(sppLineData[-1]) #Last column is the logistic value
    #Get values from the prj line; convert from scientific notation, if needed
    prjProb = float(prjLine)
    #Calculate uplift
    uplift = prjProb - curProb
    #Write outputs to file
    f.write("%s,%2.5f,%2.5f,%2.5f\n" %(gridCode,curProb,prjProb,uplift))

f.close()


