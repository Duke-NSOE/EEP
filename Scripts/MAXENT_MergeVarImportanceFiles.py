# MAXENT_MergeVarImportanceFiles.py
#
# Description: Merges and averages all the variable importance files for
#  a set of species. 
#
# Inputs:
#    The master list of variables (ResponseVars.xlsx in Data Folder)
#    Folder containing Variable Importance CSVs for the modeled species.
#
# Output is a single CSV listing each value and the averages of:
#  - Percent contribution               (spp_PC)
#  - Permeability importance            (spp_PI)
#  - Model gain without the variable    (spp_WOut)
#  - Model gain with only the variable  (spp_Only)
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
msg("...getting species fileds")
arcpy.env.workspace = sppCSVFolder
csvFiles = arcpy.ListFiles("*MEVars.csv")
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
    sppName = sppCSV.replace('_MEVars.csv','')
    msg("      processing {}".format(sppName))
    #Make a local copy (for joining)
    sppTbl = arcpy.CopyRows_management(sppCSV, "in_memory/spp")
    #Join the fields
    arcpy.JoinField_management(varTbl,"Variable",sppTbl,"Variable",("Contribution;PermImportance;GainWithout;GainWithonly"))
    #Rename the joined fields
    arcpy.AlterField_management(varTbl,"Contribution","{0}_PC".format(sppName))
    arcpy.AlterField_management(varTbl,"PermImportance","{0}_PI".format(sppName))
    arcpy.AlterField_management(varTbl,"GainWithout","{0}_WOut".format(sppName))
    arcpy.AlterField_management(varTbl,"GainWithonly","{0}_WOnly".format(sppName))
    #Add fields to output field list
    outFields.append("{0}_PC".format(sppName))
    outFields.append("{0}_PI".format(sppName))
    outFields.append("{0}_WOut".format(sppName))
    outFields.append("{0}_WOnly".format(sppName))

# Initialize the output CSV file
msg("...initializing output CSV")
f = open(outCSV,'wb')
writer = csv.writer(f)
writer.writerow([outFields[0]]+["mean_PctContribution","mean_PermImportance","mean_GainWithOut","mean_GainWithOnly"]+outFields[1:])

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
    PCsum = 0
    PIsum = 0
    GWsum = 0
    GOsum = 0
    counter = 0
    #Calculate running sums 
    for PCidx in range(1,len(outValues),4):
        PCsum += float(outValues[PCidx])
        PIsum += float(outValues[PCidx + 1]) #index offest = 1
        GWsum += float(outValues[PCidx + 2]) #index offest = 2
        GOsum += float(outValues[PCidx + 3]) #index offest = 3
        counter += 1
    #Calculate averages from the sums
    PCavg = PCsum / counter
    PIavg = PIsum / counter
    GWavg = GWsum / counter
    GOavg = GOsum / counter
    #Write values to CSV
    writer.writerow([outValues[0]]+[PCavg,PIavg,GWavg,GOavg]+outValues[1:])
    
f.close()