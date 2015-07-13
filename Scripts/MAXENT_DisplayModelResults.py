# MAXENT_DisplayModelResults.py
#
# Merges Maxent result tables to the catchment feature class to display results
#
# Spring 2015
# John.Fay@duke.edu

import arcpy, sys, os, csv
arcpy.env.overwriteOutput = 1

# Input variables
CatchmentFC = r"C:\WorkSpace\EEP_Spring2015\EEP_Tool\Data\EEP_030501.gdb\EnvStats"
maxentFolder = r"C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\Nocomis_leptocephalus\Output"

# Output
outFC = r"C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\Nocomis_leptocephalus\HabModel.shp"

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
## Get the MaxEnt result files
#Get the species name from the maxent log file
f = open(os.path.join(maxentFolder,"maxent.log"))
lines = f.readlines()
f.close()
sppLine = lines[11]
sppName = sppLine[9:-1]

#Get the result filenames
resultsFN = os.path.join(maxentFolder,"maxentResults.csv")
logisticFN = os.path.join(maxentFolder,sppName+".csv")
predictionFN = os.path.join(maxentFolder,sppName+"_samplePredictions.csv")

#Get the threshold (column 255 in the maxentResults.csv)
f = open(resultsFN,'rt')
reader = csv.reader(f)
row1 = reader.next()
row2 = reader.next()
threshold = row2[254]
f.close()

#Create a table of from the logistic CSV
logTbl = arcpy.CopyRows_management(logisticFN,"in_memory/Logistic")

#Get the logistic field name
logFld = arcpy.ListFields(logTbl)[-1].name

#Copy the Feature class
arcpy.CopyFeatures_management(CatchmentFC, outFC)

#Remove all but the first three fields
for fld in arcpy.ListFields(outFC)[3:]:
    arcpy.DeleteField_management(outFC, fld.name)

#Join the logistical output
arcpy.JoinField_management(outFC,"GRIDCODE",logTbl,"X",logFld)

#Add a new field for binary habitat
arcpy.AddField_management(outFC,"Habitat","SHORT")

#Select Rows above the threshold
whereClause = '"{}" >= {}'.format(logFld[:10],threshold)
habRecs = arcpy.MakeFeatureLayer_management(outFC,"selRecs",whereClause)

#Calculate the new field
arcpy.CalculateField_management(habRecs,"Habitat",1)