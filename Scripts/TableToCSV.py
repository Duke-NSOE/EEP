# TableToCSV.py
#
# Description: Converts a table to a comma separated value file
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv

# Input variables
inputTbl = arcpy.GetParameterAsText(0)
filter = arcpy.GetParameterAsText(1)
if (filter == "#"): filter = ""

# Output variables
outputCSV = arcpy.GetParameterAsText(2)

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
# Initialize the output csv file
msg("Initializing the output CSV file")
csvFile = open(outputCSV,'wb')

# Create the CSV writer object
writer = csv.writer(csvFile, quoting=csv.QUOTE_NONNUMERIC)

# Create a list of field names
fldList = []
for fld in arcpy.ListFields(inputTbl):
    fldList.append(fld.name)

# Remove OID field name from list
fldList.remove(arcpy.Describe(inputTbl).OIDFieldName)

# Remove Shape field, if in table
if "Shape" in fldList: fldList.remove("Shape")

# Write header row to CSV file
msg("Writing headers to CSV file")
writer.writerow(fldList)

# Create a search cursor for the inputTbl
msg("Writing values to CSV file")
cursor = arcpy.da.SearchCursor(inputTbl,fldList,filter)
for row in cursor:
    writer.writerow(row)

# Close file and clean up
csvFile.close()
del cursor,row

msg("Finished")