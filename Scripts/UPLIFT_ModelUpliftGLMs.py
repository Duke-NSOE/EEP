# UPLIFT_ModelUpliftGLMs.py
#
# Re-runs GLM and RF predictions for a set of response variables modified to reflect
#  an uplift scenario. 
#
# August 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv, datetime
arcpy.env.overwriteOutput = True

# Input variables
sppName = "Nocomis_leptocephalus"
upliftCSVInput = r'C:\WorkSpace\EEP_Tool\HabitatStats\BU_ResponseVars.csv'
upliftCSV = upliftCSVInput.replace("\\","/")
statsFolder = r'C:\WorkSpace\EEP_Tool\HabitatStats'
rPath = r'C:/Program Files/R/R-3.1.1/bin/i386/R'

# Output variables
PredictionsCSV = os.path.join(statsFolder,"BU_Uplift.csv")

# Script variables
statsFolder = statsFolder.replace("\\","/")             # Folder containing data files

sppFolder = '{0}/{1}'.format(statsFolder,sppName)
RLogFile = '{0}/{1}/{1}_uplift.R'.format(statsFolder,sppName)
RDataFile = '{0}/{1}/.RData'.format(statsFolder,sppName)

## ---Functions---
def msg(txt,type="message"):
    if type == "message":
        arcpy.AddMessage("   "+txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)
    print txt

def r(rCMD,logFN=RLogFile): #Runs an R command
    rawOutput = runR(rCMD)
    outLines = rawOutput.split("\n")
    #Print the first line
    firstLine = "[R:]"+outLines[0][5:-3]
    arcpy.AddWarning(firstLine)
    print firstLine
    #If a logfile is provided, open it, append the line, and close
    if logFN:
        log = open(logFN,'a')
        log.write("{}\n".format(firstLine[4:]))
        log.close()
    #Print any additional lines
    for idx in range(1,len(outLines)):
        if len(outLines[idx]) > 0:
            otherLine = "   "+outLines[idx]
            arcpy.AddWarning(otherLine)
            print otherLine

## -- File checks --

    
# Initialize the R log file
msg("Saving R commands to {}".format(RLogFile))
logFile = open(RLogFile,"w")
timeNow = str(datetime.datetime.now())[:-7]
logFile.write("#R uplift log file for {}; Created: {}\n".format(sppName,timeNow))
logFile.close()

#Fire up PypeR
try:
    import pyper
    #Set the R workspace
    msg("Setting the R workspace")
    runR = pyper.R(RCMD=rPath)
except:
    msg("The PyPer module is not installed.\nExiting.","error")
    sys.exit()

## -- Procedures --
#Set the R workspace
msg("Setting the R workspace")
r('setwd("{}")'.format(sppFolder))

#Load the workspace
msg("Loading the R workspace")
r('load("{}")'.format(RDataFile))

#Read in the uplift CSV file
msg("Reading in the species data")
r('upliftAll <- read.csv("{}")'.format(upliftCSV))

#Calculate predictions using the GLM object
msg("Calculating habitat likelihoods under alternate scenarios")
r('upliftPrediction <- predict(sppGLM, type="response", newdata=upliftAll)')

#Create output table
msg("Forming output table")
r('upliftTbl <- cbind(upliftAll$GRIDCODE,upliftPrediction)')
r('colnames(upliftTbl) <- c("GRIDCODE","PROB")')

#Write output table
msg("Writing output to {}".format(PredictionsCSV))
r('write.csv(upliftTbl,"{}")'.format(PredictionsCSV))

