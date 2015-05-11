# MAXENT_CreateSWDFile.py
#
# Description:
#  Takes the output CSV of the EEP Habitat Models for a given HUC6
#  and creates an input file for a given species to run in MaxEnt.
#  The format will be three columns: Species, X, and Y; however, since
#  actual coordinates are not important, we will use x = GRIDCODE and
#  Y = 
#
# Spring 2015
# John.Fay@Duke.edu

import sys, os, csv, arcpy

# Input variables
csvFile = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\030501.csv'
species = 'Nocomis_leptocephalus'
whereClause = ''

# Output variables
maxentFile = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\species.csv'

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
# Initialize the output file and its writer object
outCSV = open(maxentFile,'wb')
writer = csv.writer(outCSV)

# Write the header line
writer.writerow(("species","X","Y"))

# Loop through records in the csvFile
cursor = arcpy.da.SearchCursor(csvFile,["GRIDCODE","FEATUREID",species],whereClause)
for row in cursor:
    if row[2] == 1: dataList = (species,row[0],row[1])
    else: dataList = ("background",row[0],row[1])
    writer.writerow(dataList)

outCSV.close()
