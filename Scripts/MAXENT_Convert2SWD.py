# MAXENT_Convert2SWD.py
#
# Description: Converts the output of the Create model input file (V2) to a SWD format file
#  for running with MaxEnt.
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv
arcpy.env.overwriteOutput = True

# Input variables
statsfileCSV = arcpy.GetParameterAsText(0)   # CSV file of species and response variables
speciesName = arcpy.GetParameterAsText(1)    # Species to model; this should be a field in the above table
correlationsCSV = arcpy.GetParameterAsText(2)# CSV file listing all response variables correlated with presence/absence

#statsfileCSV = r'C:\WorkSpace\EEP_Tool\MaxEnt\Notropis_chlorocephalus\AllHUC8Records.csv'
#speciesName = 'Notropis_chlorocephalus'
#correlationsCSV = r'C:\WorkSpace\EEP_Tool\MaxEnt\Notropis_chlorocephalus\Correlations.csv'

# Output variables
outputCSV = arcpy.GetParameterAsText(3) #Output SWD format CSV file to create
#outputCSV = r'C:\WorkSpace\EEP_Tool\MaxEnt\Notropis_chlorocephalus\SWD.csv'

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
#--Get a list of fields to process from the correlations CSV file
msg("Reading field names from {}".format(correlationsCSV))
#Initialize the list
fldList = []
#Open the CSV file and create a reader object
f = open(correlationsCSV,'rt')
reader = csv.reader(f)
#Add fields to the list
for row in reader:
    fldList.append(row[0])
f.close()
#Remove the "variable" field heading"
fldList.remove("variable")
msg("{} fields included in SWD file".format(len(fldList)))

#--Initialize the output CSV
f = open(outputCSV,'wb')
writer = csv.writer(f)
writer.writerow(["Species","X","Y"]+fldList)

#Convert CSV to a temp table
sppTbl = arcpy.CopyRows_management(statsfileCSV,"in_memory/SppTble")

#Initialize presence and absence tally variables
sppTally = 0
absTally = 0

#--Extract records to a new CSV, changing species names and removing columns
msg("Writing data to {}".format(outputCSV))
cur = arcpy.da.SearchCursor(sppTbl,["Species","GRIDCODE","REACHCODE"]+fldList)            
for row in cur:
    values = list(row)
    if values[0] == 1:
        values[0] = speciesName
        sppTally += 1
    else:
        values[0] = "background"
        absTally += 1
    writer.writerow(values)

f.close()

msg("{} observations and {} pseudo absences added".format(sppTally,absTally))