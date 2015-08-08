# RF_MergeVariableImportanceFiles.py
#
# Description: Merges and averages all the RF Variable Importance tables
#   found in the supplied folder. **These should have a _RFVars.csv ending.**
#
# Inputs:
#    The master list of variables (ResponseVars.xlsx in Data Folder)
#    Folder containing Variable Importance CSVs for the modeled species.
#
# Output is a single CSV listing each value and the averages of:
#  - Model decrease in accuracy  (spp_Acc)
#  - Model Gini coefficient      (spp_Gini)
#
# July 2015
# John.Fay@duke.edu

import arcpy, sys, os, csv
arcpy.env.overwriteOutput = 1

# Input variables
variablesTbl = arcpy.GetParameterAsText(0)
sppCSVFolder = arcpy.GetParameterAsText(1)

# Output
outCSV = arcpy.GetParameterAsText(2)  

# ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)

# ---Processes---
# Get the list of Variable Importance CSVs in the folder
msg("...getting RF variable importance files")
arcpy.env.workspace = sppCSVFolder
csvFiles = arcpy.ListFiles("*_RFVars.csv")
msg("   ...{} species files accessed".format(len(csvFiles)))

# Make a copy of the master variables table
msg("...internalizing variables")
varTbl = arcpy.CopyRows_management(variablesTbl,"in_memory/vars")

# Initialize output field list; this will be used when writing the output CSV
outFields = ["variable"]

# Loop through each CSV and join it to the copy
msg("...looping through species files")
for sppCSV in csvFiles:
    #Extract the species name
    sppName = sppCSV.replace('_RFVars.csv','')
    msg("      processing {}".format(sppName))
    #Make a local copy (for joining)
    sppTbl = arcpy.CopyRows_management(sppCSV, "in_memory/spp")
    #Join the fields
    arcpy.JoinField_management(varTbl,"Variable",sppTbl,"Field1",("MeanDecreaseAccuracy;MeanDecreaseGini"))
    #Rename the joined fields
    arcpy.AlterField_management(varTbl,"MeanDecreaseAccuracy","{0}_Acc".format(sppName))
    arcpy.AlterField_management(varTbl,"MeanDecreaseGini","{0}_Gini".format(sppName))
    #Add fields to output field list
    outFields.append("{0}_Acc".format(sppName))
    outFields.append("{0}_Gini".format(sppName))

# Initialize the output CSV file
msg("...initializing output CSV")
f = open(outCSV,'wb')
writer = csv.writer(f)
writer.writerow([outFields[0]]+["mean_Acc","mean_Gini"]+outFields[1:])

# Write the data to the file
msg("...writing data to CSV")
cur = arcpy.da.SearchCursor(varTbl,outFields)
for row in cur:
    #Replace null values with zeros
    outValues = []
    for val in row:
        if not val: outValues.append(0)
        else: outValues.append(val)
    #Initialize output variables
    ACCsum = 0
    GINIsum = 0
    counter = 0
    #Calculate running sums 
    for idx in range(1,len(outValues),2):
        ACCsum += float(outValues[idx])
        GINIsum += float(outValues[idx + 1]) #index offest = 1
        counter += 1
    #Calculate averages from the sums
    ACCavg = ACCsum / counter
    GINIavg = GINIsum / counter
    #Write values to CSV
    writer.writerow([outValues[0]]+[ACCsum,GINIsum]+outValues[1:])
    
f.close()