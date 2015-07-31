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
sppName = arcpy.GetParameterAsText(0)
statsFolder = arcpy.GetParameterAsText(1)
rPath = arcpy.GetParameterAsText(2) #r'C:/Program Files/R/R-3.1.1/bin/i386/R' 

# Output variables
outJFile = arcpy.GetParameterAsText(3)

## ---Functions---
def msg(txt,type="message"):
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)
    print txt

def r(rCMD): #Runs an R command
    rawOutput = runR(rCMD)
    outLines = rawOutput.split("\n")
    #Print the first line
    firstLine = "   [R:]"+outLines[0][5:-3]
    arcpy.AddWarning(firstLine)
    print firstLine
    #Print any additional lines
    for idx in range(1,len(outLines)):
        if len(outLines[idx]) > 0:
            otherLine = "       "+outLines[idx]
            arcpy.AddWarning(otherLine)
            print otherLine

## -- Module checks --
# Set and check species SWD file
statsFolder = statsFolder.replace("\\","/")
speciesCSV = '{0}/{1}/{1}_SWD.csv'.format(statsFolder,sppName)
if not os.path.exists(speciesCSV):
    msg("SWD file not found at {}".format(speciesCSV),"error")
    sys.exit(1)
# Maxent batch file (used to identify and remove redundant fields       
maxentFile = '{0}/{1}/RunMaxent.bat'.format(statsFolder,sppName)
if not os.path.exists(maxentFile):
    msg("Maxent Batch file not found at {}".format(maxentFile),"error")
    sys.exit(1)

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
        msg("    {} is redundant".format(layerName))
        removeString += '"{}",'.format(layerName)
removeString = removeString[:-1] + ')'

#Create the SHcor function
msg("Constructing the jackGLM function")
r('''jackGLM <- function(spp, data)
	# the inputs: spp=presence/absence of a species, coded 1/0;
	# data is a frame of predictor variables
{
	# the D2 and P-value for the full model:
	full<-rep(NA,2)
	names(full)<-c("D2","P")
	# build a table for the jack-knifed estimates of explanatory power:
	nv <- ncol(data)
	d2in<-rep(NA,nv) # R2 as deviance explained by the model with only this variable
	pin<-rep(NA,nv)	# P-value for this model
	d2out<-rep(NA,nv)  # R2 for the model with this variable withheld (all other vars in)
	pout<-rep(NA,nv)  # P-value for this model
	jtable<-data.frame(cbind(d2in,pin,d2out,pout))
	vn <- names(data)
	names(jtable)<-c("D2only","Ponly","dD2without","Pwithout")
	rownames(jtable)<-vn

    # run the full model:
    gfull<-glm(as.factor(spp)~.,data=data,family=binomial)
    # D2 and P for the full model:
    d2full <- 1 - (gfull$deviance/gfull$null)
    pfull <- 1 - pchisq(gfull$null - gfull$deviance, (nv+1))
    full<-c(d2full,pfull)

    # do each variable ...
        for (i in 1:nv) {
        # this variable only in the model:
        gin<-glm(as.factor(spp)~data[,i],family=binomial)
        # D2:
        d2ii<- 1 - (gin$deviance/gin$null)
        # P-value:
        pii<- 1 - pchisq(gin$null - gin$deviance, 2)
        jtable[i,1]<-d2ii
        jtable[i,2]<-pii
        # everything except this variable:
        gix<-glm(as.factor(spp)~.,data=data[,-i],family=binomial)
        d2ix<- 1 - (gix$deviance/gix$null)
        dd2ix<-d2full-d2ix # we want the difference in D2 from the full model
        aix<-anova(gix,gfull,test="Chi") # does this variable add to the model?
        pix<-aix$"Pr(>Chi)"[[2]] # the P-value on the 2nd model, with the variable added
        jtable[i,3]<-dd2ix
        jtable[i,4]<-pix
    }
    return(list(full,jtable=jtable))
}
''')

#Set the R workspace
msg("Setting the R workspace")
r('setwd("{}")'.format(os.path.dirname(speciesCSV)))

#Read in the CSV file
msg("Reading in the species data")
r('sppAll <- read.csv("{}")'.format(os.path.basename(speciesCSV)))

#Set the spp vector
msg("Create species vector: 'spp'")
r('spp <- sppAll[,c(1)]')

#Set the data matrix
#msg("Create response variable data frame: 'habData'")
r('habData <- sppAll[,c(-1,-2,-3)]')

#Drop redundant fields
if len(removeString) > 16:
    msg("Dropping redundant fields from data frame")
    r(removeString)
    r('habData2 <- habData[,!(names(habData) %in% dropFields)]')

#Run the GLM
msg("Running the GLM")
r('sppGLM <- glm(as.factor(spp)~., data=habData2, family=binomial)')
#r('summary(sppGLM'))
r('sppGLMAnova <- anova(sppGLM, test="Chi")')
r('sppGLMd2 <- 1-(sppGLM$deviance/sppGLM$null.deviance)')
#r('sppGLMd2')
#r('source("C:/WorkSpace/EEP_Tool/Scripts/RScripts/jackGLM.R")')
r('sppJtable <- jackGLM(spp,habData2)')
#r('sppJtable')
msg("Writing jackknife results to {}".format(outJFile))
r('write.csv(sppJtable$jtable, "{}")'.format(outJFile))
