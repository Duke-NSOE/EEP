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

import sys, os, arcpy, csv, datetime

# Input variables
sppName = arcpy.GetParameterAsText(0)
statsFolder = arcpy.GetParameterAsText(1)
rPath = arcpy.GetParameterAsText(2) #r'C:/Program Files/R/R-3.1.1/bin/i386/R'

# Static inputs in species folder
sppPath = os.path.join(statsFolder,sppName)
speciesCSV = os.path.join(sppPath,'{0}_SWD.csv'.format(sppName))   # Maxent SWD file containing all data to run the models
maxentFile = os.path.join(sppPath,'RunMaxent.bat')                  # MaxEnt batch file, containing response vars to exclude
correlationsCSV = os.path.join(sppPath,'SH_Correlations.csv')      # List of response variables correlated with presence/absence
                          
# Output variables
GLMAnovaCSV = os.path.join(sppPath,"GLM_Anova.csv")              #GLM ANOVA Table
GLMPredictionsCSV = os.path.join(sppPath,"GLM_Predictions.csv")  #GLM Predictions
RFVarImportanceCSV = os.path.join(sppPath,"RF_VarImportance.csv")     #RF variable importance table
RFPredictionsCSV = os.path.join(sppPath,"RF_Predictions.csv")    #RF Predictions
GLMconfusionCSV = os.path.join(sppPath,"GLM_Confusion.csv")      #Stores the GLM confusion matrix
GLMsummaryCSV = os.path.join(sppPath,"GLM_Summary.csv")          #Stores the GLM deviance and the cutoff
RFconfusionCSV = os.path.join(sppPath,"RF_Confusion.csv")        #Stores the RF confusion matrix
RLogFile = os.path.join(sppPath,"{}.R".format(sppName))         #R Log file; can be open in R to re-run model
RDataFile = os.path.join(sppPath,"{}.RData".format(sppName))    #R workspace; used later to run projections
                              
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

def r(rCMD,logFN=RLogFile): #Runs an R command
    rawOutput = runR(rCMD)
    outLines = rawOutput.split("\n")
    #Print the first line
    firstLine = "[R:]"+outLines[0][5:-3]
    arcpy.AddWarning(firstLine)
    print firstLine
    #If a logfile is provided, open it, append the line, and close
    if RLogFile:
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
# Set and check species jackGLM R script
if not os.path.exists(jackGLM):
    msg("jackGLM R script not found at {}".format(jackGLM),"error")
    sys.exit(1)
# Set and check species cutoffROCR R script
if not os.path.exists(cutoffROCR):
    msg("cutoffROCR R script not found at {}".format(cutoffROCR),"error")
    sys.exit(1)
# Set and check species SWD file
if not os.path.exists(speciesCSV):
    msg("SWD file not found at {}".format(speciesCSV),"error")
    sys.exit(1)
# Maxent batch file (used to identify and remove redundant fields       
if not os.path.exists(maxentFile):
    msg("Maxent Batch file not found at {}".format(maxentFile),"error")
    sys.exit(1)

# Initialize the R log file
msg("Saving R commands to {}".format(RLogFile))
logFile = open(RLogFile,"w")
timeNow = str(datetime.datetime.now())[:-7]
logFile.write("#R log file for {}; Created: {}\n".format(sppName,timeNow))
logFile.close()

#Fire up PypeR
try:
    import pyper
    #Set the R workspace
    msg("Setting the R workspace")
    runR = pyper.R(RCMD=rPath)
except:
    msg("The PyPer module is not installed.\nExiting.","error")
    msg("Check the path: {}".format(rPath))
    sys.exit()

## -- Procedures --
#Set the R workspace
msg("Setting the R workspace")
r('setwd("{}")'.format(os.path.dirname(speciesCSV)))

#Read in the CSV file
msg("Reading in the species data")
r('sppAll <- read.csv("{}")'.format(os.path.basename(speciesCSV)))

#Set the spp vector
msg("Creating species vector: 'spp'")
r('spp <- sppAll[,c(1)]')

#Make a binary vector of spp
r('sppBin = c(spp)')
#Replace 1s with 0s and 2s with 1s
r('sppBin <- replace(sppBin, sppBin == 1, 0)')
r('sppBin <- replace(sppBin, sppBin == 2, 1)')

#Make a dictionary of correlation values from the Correlations.csv file
msg("Reading in variable correlations with presence-absence")
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

#Create the R command to set the habData data frame
commandString = "habData <- sppAll[c("
for var in varList:
    commandString += '"{}",'.format(var)
commandString = commandString[:-1] #remove ending comma
commandString += ")]"

#Run the command to create the habData data frame
msg("Creating the response variable data frame")
r(commandString)

#Load the jackknife scripe
#msg("Loading jackGLM script")
#r('source("{}")'.format(jackGLM))

#Run the GLM
msg("Running the GLM")
r('sppGLM <- glm(as.factor(spp)~., data=habData, family=binomial)')
#r('summary(sppGLM'))
msg("Computing ANOVA on GLM model and saving to file...")
r('sppGLMAnova <- anova(sppGLM, test="Chi")')
r('write.csv(sppGLMAnova, "{}")'.format(GLMAnovaCSV))
msg("Computing model deviance")
r('sppGLMd2 <- 1-(sppGLM$deviance/sppGLM$null.deviance)')
#Get the deviance as a Python variable
GLMDeviance = runR['sppGLMd2']
#r('sppGLMd2')
#r('sppJtable <- jackGLM(spp,habData)')
#r('colnames(sppJtable)[0] <- "Variable"')

#msg("Writing jackknife results to {}".format(GLMVarImportanceCSV))
#r('write.csv(sppJtable$jtable, "{}")'.format(GLMVarImportanceCSV))

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
#Save the cutoff as a Python variable
r('cutoff <- cutoff.ROCR(sppPred, "tpr", target=0.95)')
GLMCutoff = runR['cutoff']
r('sppPredGLM[sppPredGLM < cutoff] <- 0')
r('sppPredGLM[sppPredGLM >= cutoff] <- 1')

#Generate the confusion matrix
r('cfGLM <- table(sppPredGLM,spp)')
msg("Writing GLM confusion matrix to {}".format(GLMconfusionCSV))
r('write.csv(cfGLM,"{}")'.format(GLMconfusionCSV))

msg("Writing GLM predictions to {}".format(GLMPredictionsCSV))
#Merge the sppAll gridcode, predictions, and thresholded values
r('outTableGLM <- cbind(sppAll$X,sppGLM$fitted.values,sppPredGLM,sppBin)')
#Rename columns
r('colnames(outTableGLM)[0] <- "ID"')
r('colnames(outTableGLM)[1] <- "GRIDCODE"')
r('colnames(outTableGLM)[2] <- "HAB_PROB"')
r('colnames(outTableGLM)[3] <- "PREDICTION"')
r('colnames(outTableGLM)[4] <- "OBSERVED"')
#Write the output
r('write.csv(outTable,"{}")'.format(GLMPredictionsCSV))

#Write the model summary
msg("Writing model summary: {}".format(GLMsummaryCSV))
f = open(GLMsummaryCSV,'w')
f.write("GLM Model, {}\n".format(sppName))
f.write("Model deviance, %2.6f\n" %GLMDeviance)
f.write("Model cutoff, %2.6f\n" %GLMCutoff)
f.close()

##-- RANDOM FOREST --
msg("Running random forest analysis")
r('library(randomForest)')
r('sppForest <- randomForest(as.factor(spp)~., data=habData, ntree=501, importance=TRUE)')
msg("Compiling variable importances to {}".format(RFVarImportanceCSV))
r('outTableRFVars <- sppForest$importance')
#r('colnames(outTableRFVars)[0] <- "VARIABLE"')
#r('colnames(outTableRFVars)[1] <- "0"')
#r('colnames(outTableRFVars)[2] <- "1"')
r('write.csv(outTableRFVars,"{}")'.format(RFVarImportanceCSV))
msg("Running predictions on catchments")
#Calculate RF Predictions (continuous)
r('rfProbs <- predict(sppForest, type="prob")')
#Calculate Responses (binary)
r('rfPredictions <- predict(sppForest, type="response")')
#--Convert rfPredictions to binary
r('rfPredBin = c(rfPredictions)')
#--Replace 1s with 0s and 2s with 1s
r('rfPredBin <- replace(rfPredBin, rfPredBin == 1, 0)')
r('rfPredBin <- replace(rfPredBin, rfPredBin == 2, 1)')
#Write to a table
r('outTableRF <- cbind(sppAll$X,rfProbs[,(2)],rfPredBin,sppBin)')
r('colnames(outTableRF)[1] <- "GRIDCODE"')
r('colnames(outTableRF)[2] <- "HABPROB"')
r('colnames(outTableRF)[3] <- "PREDICTION"')
r('colnames(outTableRF)[4] <- "OBSERVED"')
r('write.csv(outTableRF,"{}")'.format(RFPredictionsCSV))

#Generate the confusion matrix
r('cfRF <- table(rfPredictions,spp)')
msg("Writing RF confusion matrix to {}".format(RFconfusionCSV))
r('write.csv(cfRF,"{}")'.format(RFconfusionCSV))

#Save the workspace
msg("Saving the workspace to {}".format(RDataFile))
r('save.image()')
