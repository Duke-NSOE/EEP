# STATS_GLM.py
#
# Runs GML using SciPy and StatsModel modules
#
#  *****************************************************************************
#  ** This module requires the SciPy module to be installed. When installing, **
#  ** be sure to get version 0.12.0 as that is the one that works with the    **
#  ** version of NumPy that is installed with ArcGIS 10.2                     ** 
#  *****************************************************************************
#
# SciPy URL:      http://sourceforge.net/projects/scipy/files/scipy/0.12.0/
# 
# July 2015
# John.Fay@duke.edu

import sys, os, arcpy

# Input variables
rPath = r'C:/Program Files/R/R-3.1.1/bin/i386/R' #arcpy.GetParameterAsText(0)
speciesCSV = r'C:\WorkSpace\EEP_Tool\MaxEnt\Nocomis_leptocephalus\Nocomis_leptocephalus_GLMin.csv' #arcpy.GetParameterAsText(1)
maxentFile = r'C:\WorkSpace\EEP_Tool\MaxEnt\Nocomis_leptocephalus\RunMaxent.bat'
sppName ="Nocomis_leptocephalus"

## ---Functions---
def msg(txt,type="message"):
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)
    elif type == 'r':
        arcpy.AddWarning("[R:]"+txt[5:-4])
        txt = "[R:]"+txt[5:-4]
    print txt

def r(rCMD): #Runs an R command
    rawOutput = runR(rCMD)
    outLines = rawOutput.split("\n")
    #Print the first line
    firstLine = "[R:]"+outLines[0][5:-3]
    arcpy.AddWarning(firstLine)
    print firstLine
    #Print any additional lines
    for idx in range(1,len(outLines)):
        if len(outLines[idx]) > 0:
            otherLine = "    "+outLines[idx]
            arcpy.AddWarning(otherLine)
            print otherLine

## -- Module checks --
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
#Get the fields to cut from the MaxEnt batch file
f = open(maxentFile,'rt')
lineString = f.readline()
f.close()
removeString = "dropFields <- c("
for item in lineString.split(" "):
    if 'togglelayerselected' in item:
        layerName = item.split("=")[-1]
        #msg("{} is redundant".format(layerName))
        removeString += '"{}",'.format(layerName)
removeString = removeString[:-1] + ')'

#Set the R workspace
msg("Setting the R workspace")
r('setwd("{}")'.format(os.path.dirname(speciesCSV)))

#Read in the CSV file
msg("Reading in the species data")
r('sppAll <- read.csv("{}")'.format(os.path.basename(speciesCSV)))

#Set the spp vector
msg("Create species vector: 'spp'")
r('spp <- sppAll[,c(1)]')

#Change levels to binary
#r('levels(spp)[levels(spp)=="{}"] <- 1'.format(sppName))
#r('levels(spp)[levels(spp)=="background"] <- 0')
    
#Change the spp values
#r('spp2 <- gsub("Nocomis_leptocephalus",1,spp)')
#r('spp3 <- gsub("background",0,spp2)'))

#Set the data matrix
#msg("Create response variable data frame: 'habData'")
r('habData <- sppAll[,c(-1,-2,-3)]')

#Drop redundant fields
msg("Dropping redundant fields from data frame")
r(removeString)
r('habData2 <- habData[,!(names(habData) %in% dropFields)]')

#Run the GLM
msg("Running the GLM")
r('sppGLM <- glm(as.factor(spp)~., data=habData2, family=binomial)')

#r('summary(sppGLM'))
r('sppGLMAnova <- anova(sppGLM, test="Chi")')
r('sppGLMd2 <- 1-(sppGLM$deviance/sppGLM$null.deviance)')
r('sppGLMd2')
r('source("C:/WorkSpace/EEP_Tool/Scripts/RScripts/jackGLM.R")')
r('sppJtable <- jackGLM(spp,habData2)')
r('sppJtable')
r('write.csv(sppJtable, "{}_jtable.csv")'.format(sppName))
