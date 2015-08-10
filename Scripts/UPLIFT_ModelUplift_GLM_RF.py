# UPLIFT_ModelUpliftGLMs.py
#
# Description: Re-runs GLM and RF predictions for all HUCs in supplied CSV files.
#   First runs a prediction for the "currentCSVInput" file
#
# August 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv, datetime
arcpy.env.overwriteOutput = True

# Input variables
sppName = arcpy.GetParameterAsText(0)#"Nocomis_leptocephalus"
upliftPrefix = arcpy.GetParameterAsText(1)#"BU"
currentCSV = arcpy.GetParameterAsText(2)#r'C:\WorkSpace\EEP_Tool\HabitatStats\Current_ResponseVars.csv'
altCSV = arcpy.GetParameterAsText(3)#r'C:\WorkSpace\EEP_Tool\HabitatStats\BU_ResponseVars.csv'
statsFolder = arcpy.GetParameterAsText(4)#r'C:\WorkSpace\EEP_Tool\HabitatStats'
rPath = arcpy.GetParameterAsText(5)#r'C:/Program Files/R/R-3.1.1/bin/i386/R'

# Replace backslashes with forward slashes to work with R
currentCSV = currentCSV.replace("\\","/")
altCSV = altCSV.replace("\\","/")
statsFolder = statsFolder.replace("\\","/") 

# Output variables
PredictionsCSV = os.path.join(statsFolder,"{}_{}.csv".format(upliftPrefix,sppName))
arcpy.SetParameterAsText(6,PredictionsCSV)

# Script variables
sppFolder = '{0}/{1}'.format(statsFolder,sppName)               #Folder containing species stats
RLogFile = '{0}/{1}/{1}_uplift.R'.format(statsFolder,sppName)   #Log file to record R commands
RDataFile = '{0}/{1}/.RData'.format(statsFolder,sppName)        #Data file containing previous r objects

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
# Make sure the RData file exists
if not os.path.exists(RDataFile):
    msg("RData file not found at {}".format(RDataFile),"error")
    sys.exit(1)
    
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

#Read in the current data CSV file
msg("Reading in the alt data")
r('currentAll <- read.csv("{}")'.format(currentCSV))

#Read in the alt data CSV file
msg("Reading in the alt data")
r('altAll <- read.csv("{}")'.format(altCSV))

##--GLM--
#Calculate predictions using the GLM object
msg("GLM: Calculating habitat likelihoods under current conditions")
r('currentPredictionGLM <- predict(sppGLM, type="response", newdata=currentAll)')

#Calculate predictions using the GLM object
msg("GLM: Calculating habitat likelihoods under alternate scenarios")
r('altPredictionGLM <- predict(sppGLM, type="response", newdata=altAll)')

#Calculate the difference
msg("Computing uplift")
r('{}_upliftGLM <- altPredictionGLM - currentPredictionGLM'.format(upliftPrefix))

##--RANDOM FOREST--
#Load the RandomForest library
r('library(randomForest)')

#Calculate predictions using the GLM object
msg("RF: Calculating habitat likelihoods under current conditions")
r('currentPredictionRF <- predict(sppForest, type="prob", newdata=currentAll)')

#Calculate predictions using the GLM object
msg("GLM: Calculating habitat likelihoods under alternate scenarios")
r('altPredictionRF <- predict(sppForest, type="prob", newdata=altAll)')

#Calculate the difference
msg("Computing uplift")
r('{}_upliftRF <- altPredictionRF[,1] - currentPredictionRF[,1]'.format(upliftPrefix))

##--OUTPUT--
#Create output table
msg("Forming output table")
r('GRIDCODE <- currentAll$GRIDCODE')
r('upliftTbl <- cbind(GRIDCODE, {0}_upliftGLM, {0}_upliftRF)'.format(upliftPrefix))

#Write output table
msg("Writing output to {}".format(PredictionsCSV))
r('write.csv(upliftTbl,"{}")'.format(PredictionsCSV))

