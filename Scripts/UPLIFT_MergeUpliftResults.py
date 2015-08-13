# UPLIFT_MergeUpliftResults.py
#
# Description:
#  Merges uplift tables for multiple species into a single table
#
# Summer 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv, tempfile
arcpy.env.overwriteOutput = 1

# Input variables
scenarioPrefix = arcpy.GetParameterAsText(0)
scenarioFldr = arcpy.GetParameterAsText(1)
catchmentsFC = arcpy.GetParameterAsText(2)

# Output variables
outCSV = arcpy.GetParameterAsText(3)

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
#Get a list of scenario uplift files
arcpy.env.workspace = scenarioFldr
meFiles = arcpy.ListFiles("*{}_maxent.csv".format(scenarioPrefix)) #Maxent results
glmFiles = arcpy.ListFiles("*{}_glmrf.csv".format(scenarioPrefix)) #GLM/RF results

# Make a copy of the master variables table
msg("...internalizing variables")
varTbl = arcpy.CopyRows_management(catchmentsFC,"in_memory/vars")

# Create an attribute index
#msg("...adding attribute index to speed processing")
#arcpy.AddIndex_management(varTbl,"GRIDCODE","GRIDCODE","UNIQUE")

# Initialize outFields list - list of fields to write out
outFields = ["GRIDCODE"]

# Loop through each CSV and join it to the copy
msg("...looping through uplift files")
for meFile in meFiles:
    #Get the corresponding GLM file; skip if not found
    glmFile = meFile.replace("maxent","glmrf")
    #Raise error if file not found
    if not glmFile in glmFiles:
        msg("     {} file not found".format(glmFile),"warning")
        continue
    
    #Extract the species name
    sppName = meFile[7:-14]
    #Shorten the spp name
    sppNames = sppName.split("_")
    sppName = sppNames[0][0]+"_"+sppNames[1][:5]

    #--MAXENT--
    msg("      processing {} (Maxent)".format(sppName))
    #Make a local copy (for joining)
    sppTbl = arcpy.CopyRows_management(meFile, "in_memory/spp")
    #Join the maxent fields
    arcpy.JoinField_management(varTbl,"GRIDCODE",sppTbl,"GRIDCODE","{0}_ME;{0}_uplift_ME".format(scenarioPrefix))
    #Rename the joined fields
    arcpy.AlterField_management(varTbl,"{0}_ME".format(scenarioPrefix),"{0}_LogProb_ME".format(sppName))
    arcpy.AlterField_management(varTbl,"{0}_uplift_ME".format(scenarioPrefix),"{0}_Uplift_ME".format(sppName))
    #Add fields to output field list
    outFields.append("{0}_LogProb_ME".format(sppName))
    outFields.append("{0}_Uplift_ME".format(sppName))

    #--GLM RF---
    msg("      processing {} (GLM/RF)".format(sppName))
    #Make a local copy (for joining)
    sppTbl = arcpy.CopyRows_management(glmFile, "in_memory/spp")
    #Join the GLM fields
    arcpy.JoinField_management(varTbl,"GRIDCODE",sppTbl,"GRIDCODE","{0}_GLM;{0}_Uplift_GLM;{0}_RF;{0}_uplift_RF".format(scenarioPrefix))
    #Rename the joined fields
    arcpy.AlterField_management(varTbl,"{0}_GLM".format(scenarioPrefix),"{0}_LogProb_GLM".format(sppName))
    arcpy.AlterField_management(varTbl,"{0}_uplift_GLM".format(scenarioPrefix),"{0}_Uplift_GLM".format(sppName))
    arcpy.AlterField_management(varTbl,"{0}_RF".format(scenarioPrefix),"{0}_LogProb_RF".format(sppName))
    arcpy.AlterField_management(varTbl,"{0}_uplift_RF".format(scenarioPrefix),"{0}_Uplift_RF".format(sppName))
    #Add fields to output field list
    outFields.append("{0}_LogProb_GLM".format(sppName))
    outFields.append("{0}_Uplift_GLM".format(sppName))
    outFields.append("{0}_LogProb_RF".format(sppName))
    outFields.append("{0}_Uplift_RF".format(sppName))

# Initialize the output CSV file
msg("...initializing output CSV")
f = open(outCSV,'wb')
writer = csv.writer(f)
writer.writerow(["GRIDCODE","mean_UpliftME","mean_UpliftGLM","mean_UpliftRF"]+outFields[1:])

# Write the data to the file
msg("...writing data to CSV")
cur = arcpy.da.SearchCursor(varTbl,outFields)
for row in cur:
    #Get the gridcode
    gridcode = row[0]
    
    #Replace null values with zeros
    outValues = []
    for val in row:
        if not val: outValues.append(0)
        else: outValues.append(val)
        
    #Initialize running sum variables
    ME_LogProbSum = 0
    ME_UpliftSum = 0
    GLM_LogProbSum = 0
    GLM_UpliftSum = 0
    RF_LogProbSum = 0
    RF_UpliftSum = 0
    counter = 0
    offSet = len(meFiles)*2 #Number of columns between 1st Maxent and 1st GLM column

    #Calculate running sums by looping through columns
    for ColIdx in range(1,len(outValues),6):
        #Running sums of LogProb values, Uplift values, and a counter to calc averages
        ME_LogProbSum += float(outValues[ColIdx])
        ME_UpliftSum += float(outValues[ColIdx + 1]) #index offest = 1
        GLM_LogProbSum += float(outValues[ColIdx + 2])
        GLM_UpliftSum += float(outValues[ColIdx + 3]) #index offest = 1
        RF_LogProbSum += float(outValues[ColIdx + 4])
        RF_UpliftSum += float(outValues[ColIdx + 5]) #index offest = 1        
        counter += 1
                              
    #Calculate averages from the sums
    ME_LogProbAvg = ME_LogProbSum / counter
    ME_UpliftAvg = ME_UpliftSum / counter
    GLM_LogProbAvg = GLM_LogProbSum / counter
    GLM_UpliftAvg = GLM_UpliftSum / counter
    RF_LogProbAvg = RF_LogProbSum / counter
    RF_UpliftAvg = RF_UpliftSum / counter

    #Write values to CSV
    writer.writerow([gridcode,ME_UpliftAvg,GLM_UpliftAvg,RF_UpliftAvg]+outValues[1:])
    
f.close()
