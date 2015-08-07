# STATS_GLM.py
#
# Description: Runs GLM using PypeR module to run R command and generates a CSV table
#  listing variable importance using the embedded jackknifing script from Dean Urban.
#
# Inputs include:
#  (1) the species name (used to locate requried input files);
#  (2) the stats folder generated in earler tool scripts. The stats folder should be the root 
#      folder containing sub-folders for all modeled species. These sub-folders *must* be named 
#      with the species name (e.g. "Nocomis_leptocephalus"), and these sub-folders *must* contain
#      the **Maxent SWD** file (e.g. "Nocomis_leptocephalus_SWD.csv" - containing the data used 
#      to run the model) and the MaxEnt batchfile (e.g., "RunMaxent.bat" - containing the
#      variables omitted because of redundancy). 
#  (3) The path to the R executable file, used to link Python to R via the PypeR module
#
# Outputs include:
#  (1) A CSV format table listing all the variables modeled and indications of variable importance
#
# July 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv

# Input variables
sppName = arcpy.GetParameterAsText(0)
statsFolder = arcpy.GetParameterAsText(1)
rPath = arcpy.GetParameterAsText(2) #r'C:/Program Files/R/R-3.1.1/bin/i386/R' 

# Output variables
GLMVarImportanceCSV = arcpy.GetParameterAsText(3)   #GLM variable importance table (Jackknife results)
GLMPredictionsCSV = arcpy.GetParameterAsText(4)     #GLM Predictions
RFVarImportanceCSV = arcpy.GetParameterAsText(5)    #RF variable importance table
RFPredictionsCSV = arcpy.GetParameterAsText(6)      #RF Predictions

# Script variables
rlibPath = os.path.join(sys.path[0],"RScripts")         # Location of all R subscripts
jackGLM = os.path.join(rlibPath,"jackGLM.R")            # Jackkinifing subscript
cutoffROCR = os.path.join(rlibPath,"cutoff.ROCR.R")     # ROCR subscript

## ---Functions---
def msg(txt,type="message"):
    if type == "message":
        arcpy.AddMessage("   "+txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)
    print txt

def r(rCMD,logging=0): #Runs an R command
    rawOutput = runR(rCMD)
    outLines = rawOutput.split("\n")
    #Print the first line
    firstLine = "[R:]"+outLines[0][5:-3]
    arcpy.AddWarning(firstLine)
    print firstLine
    #Print any additional lines
    for idx in range(1,len(outLines)):
        if len(outLines[idx]) > 0:
            otherLine = "   "+outLines[idx]
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
#Set the R workspace
msg("Setting the R workspace")
r('setwd("{}")'.format(os.path.dirname(speciesCSV)))

#Read in the CSV file
msg("Reading in the species data")
r('sppAll <- read.csv("{}")'.format(os.path.basename(speciesCSV)))

#Set the spp vector
msg("Create species vector: 'spp'")
r('spp <- sppAll[,c(1)]')

#Make a binary vector of spp
r('sppBin = c(spp)')
#Replace 1s with 0s and 2s with 1s
r('sppBin <- replace(sppBin, sppBin == 1, 0)')
r('sppBin <- replace(sppBin, sppBin == 2, 1)')

#Make a dictionary of correlation values from the Correlations.csv file
msg("Reading in variable correlations with presence-absence")
correlationsCSV = os.path.join(statsFolder,sppName,"Correlations.csv")
corDict = {}
f = open(correlationsCSV,'rt')
reader = csv.reader(f)
for row in reader:
    corDict[row[0]] = row[2]

#Create a sorted a list of variable names **on coeffient values**
msg("Sorting variables on coefficient with presence-absence")
varList = []
for key, value in sorted(corDict.iteritems(), key=lambda (k,v): (v,k)):
    varList.append(key)

#Remove "variable" from the list
if "variable" in varList: varList.remove("variable")

##REMOVE CROSSINGS
if "Crossings" in varList: varList.remove("Crossings")

#Get the fields to cut (b/c of redundancy from the MaxEnt batch file
f = open(maxentFile,'rt')
lineString = f.readline()
f.close()
#removeString = "dropFields <- c("
for item in lineString.split(" "):
    #If the item appears as a "togglelayersselected" item, it should be removed
    if 'togglelayerselected' in item:
        #Get the layer name from the string
        layerName = item.split("=")[-1]
        #Inform the user that it will not be included
        msg("    {} is redundant".format(layerName))
        #Remove the item in the varList, if it's there
        varList.remove(layerName)

#Initialize the habData object with the first column
r('habData <- sppAll[("{}")]'.format(varList[0]))

#Create the R command to set the habData data frame
commandString = "habData <- sppAll[c("
for var in varList:
    commandString += '"{}",'.format(var)
commandString = commandString[:-1] #remove ending comma
commandString += ")]"

#Run the command to create the habData data frame
msg("Creating the response variable data frame")
r(commandString)

#Create the SHcor function
msg("Loading jackGLM script")
r('source("{}")'.format(jackGLM))

#Run the GLM
msg("Running the GLM")
r('sppGLM <- glm(as.factor(spp)~., data=habData, family=binomial)')
#r('summary(sppGLM'))
#r('sppGLMAnova <- anova(sppGLM, test="Chi")')
#r('sppGLMd2 <- 1-(sppGLM$deviance/sppGLM$null.deviance)')
#r('sppGLMd2')
r('sppJtable <- jackGLM(spp,habData)')

#r('sppJtable')
msg("Writing jackknife results to {}".format(GLMVarImportanceCSV))
r('write.csv(sppJtable$jtable, "{}")'.format(GLMVarImportanceCSV))

#Run GLM predictions on current conditions
msg("Running predictions on current conditions")
r('sppPredGLM <- predict(sppGLM, type="response",data=habData)')
msg("Loading the ROCR library")
r('library(ROCR)')
msg("Loading the cutoffROCR script")
r('source("{}")'.format(cutoffROCR))
msg("Predicting values on all catchments")
r('sppPred <- prediction(sppGLM$fitted.values,spp)')
msg("Finding and applying probability cutoff (via ROC)") 
r('cutoff <- cutoff.ROCR(sppPred, "tpr", target=0.95)')
r('sppPredGLM[sppPredGLM < cutoff] <- 0')
r('sppPredGLM[sppPredGLM >= cutoff] <- 1')

msg("Writing predictions to {}".format(GLMPredictionsCSV))
#Merge the sppAll gridcode, predictions, and thresholded values
r('outTable <- cbind(sppAll$X,sppGLM$fitted.values,sppPredGLM,sppBin)')
#Rename columns
r('colnames(outTable)[0] <- "ID"')
r('colnames(outTable)[1] <- "GRIDCODE"')
r('colnames(outTable)[2] <- "HAB_PROB"')
r('colnames(outTable)[3] <- "PREDICTION"')
r('colnames(outTable)[4] <- "OBSERVED"')
#Write the output
r('write.csv(outTable,"{}")'.format(GLMPredictionsCSV))

##-- RANDOM FOREST --
msg("Running random forest analysis")
r('library(randomForest)')
r('sppForest <- randomForest(as.factor(spp)~., data=habData, ntree=500, importance=TRUE)')
msg("Compiling variable importances to {}".format(RFVarImportanceCSV))
r('outTable <- sppForest$importance')
#r('colnames(outTable)[0] <- "VARIABLE"')
#r('colnames(outTable)[1] <- "0"')
#r('colnames(outTable)[2] <- "1"')
r('write.csv(outTable,"{}")'.format(RFVarImportanceCSV))
msg("Running predictions on catchments")
r('rfPredictions <- predict(sppForest, type="response")')
r('rfProbs <- predict(sppForest, type="prob")')

r('outTable <- cbind(sppAll$X,rfProbs[,(1)],rfPredictions,sppBin)')
r('colnames(outTable)[1] <- "GRIDCODE"')
r('colnames(outTable)[2] <- "HABPROB"')
r('colnames(outTable)[3] <- "PREDICTION"')
r('colnames(outTable)[4] <- "OBSERVED"')
r('write.csv(outTable,"{}")'.format(RFPredictionsCSV))


#Remove the R object from memory
#del pyper

