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
scenarioPrefix = "BU"
scenarioFldr = r'C:\WorkSpace\EEP_Tool\HabitatStats\Scenarios'
catchmentsFC = r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\NHDCatchments'

# Output variables
outCSV = r'C:\WorkSpace\EEP_Tool\HabitatStats\Scenarios\CombinedUpliftBU.csv'

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
meFiles = arcpy.ListFiles("*{}_maxent.csv".format(scenarioPrefix))      #Maxent results
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
msg("...looping through Maxent uplift files")
for meFile in meFiles:
    #Extract the species name
    sppName = meFile[7:-14]
    msg("      processing {}".format(sppName))
    #Make a local copy (for joining)
    sppTbl = arcpy.CopyRows_management(meFile, "in_memory/spp")
    #Join the fields
    arcpy.JoinField_management(varTbl,"GRIDCODE",sppTbl,"GRIDCODE","{0}_ME;{0}_uplift_ME".format(scenarioPrefix))
    #Rename the joined fields
    arcpy.AlterField_management(varTbl,"{0}_ME".format(scenarioPrefix),"{0}_LogProb".format(sppName))
    arcpy.AlterField_management(varTbl,"{0}_uplift_ME".format(scenarioPrefix),"{0}_Uplift".format(sppName))
    #Add fields to output field list
    outFields.append("{0}_LogProb".format(sppName))
    outFields.append("{0}_Uplift".format(sppName))

# Initialize the output CSV file
msg("...initializing output CSV")
f = open(outCSV,'wb')
writer = csv.writer(f)
writer.writerow(["GRIDCODE","mean_LogProb","mean_Uplift"]+outFields[1:])

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
    #Initialize output variables
    LogProbSum = 0
    UpliftSum = 0
    counter = 0
    #Calculate running sums by looping through columns, skipping the 1st (Gridcode)
    # and skipping every other one. 
    for ColIdx in range(1,len(outValues),2):
        #Running sums of LogProb values, Uplift values, and a counter to calc averages
        LogProbSum += float(outValues[ColIdx])
        UpliftSum += float(outValues[ColIdx + 1]) #index offest = 1
        counter += 1
    #Calculate averages from the sums
    LogProbAvg = LogProbSum / counter
    UpliftAvg = UpliftSum / counter

    #Write values to CSV
    writer.writerow([gridcode,LogProbAvg,UpliftAvg]+outValues[1:])
    
f.close()