# MAXENT_ResultsToBackground.py
#
# Description: Creates two MaxEnt input CSV files from the EEP Results CSV file corresponding
#  to a selected species. The first is the species file in MaxEnt SWD (Species with data) format;
#  The second is a background file.  
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv
arcpy.env.overwriteOutput = True

# Input variables
resultsTbl = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Data\EEP_030501.gdb\results'
#arcpy.GetParameterAsText(0) #NHD catchment environment variables
speciesTbl = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Data\EEP_030501.gdb\HabModel'
# arcpy.GetParameterAsText(1) #NHD catchments tagged with species presence
speciesName = "Rhinichthys_atratulus"
# arcpy.GetParameterAsText(3) #Species to model

# Output variables
speciesCSV = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\ME_species.csv'
#arcpy.GetParameterAsText(3)    # MaxEnt species file
backgroundCSV = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\ME_background.csv'
#arcpy.GetParameterAsText(4) # MaxEnt env vars file

# Script varables
EnvVarCount = 107 ##<--Number of environment variables; after this it's species columns
sppOnlyTbl = "in_memory/SppTble"
resultsCopyTbl = "in_memory/Results2"

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
# Extract Catchments with species
arcpy.TableSelect_analysis(speciesTbl, sppOnlyTbl,'"{}" = 1'.format(speciesName))

# Make a copy of the results table and join the species table to it
arcpy.CopyRows_management(resultsTbl,resultsCopyTbl)
arcpy.JoinField_management(resultsCopyTbl,"GRIDCODE",sppOnlyTbl,"GRIDCODE","[{}]".format(speciesName))

# Create a list of field names
fldList = [species,"x","y"] #start the list with the MaxEnt format: {species, x, y}
for fld in arcpy.ListFields(resultsTbl)[:EnvVarCount]:
    fldList.append(fld.name)

## WRITE THE SPECIES FILE ##
msg("Writing the species file...")
# Initialize the species output csv file & create the writer object
msg("...Initializing the output CSV files")
csvFile = open(speciesCSV,'wb')
writer = csv.writer(csvFile, quoting=csv.QUOTE_NONNUMERIC)

# Write header row to CSV file
msg("...Writing headers to CSV file")
writer.writerow(fldList)

# Create a search cursor for the resultsTbl
msg("...Writing values to CSV file")
whereClause = '"{}" > 1'.format(speciesName)
cursor = arcpy.da.SearchCursor(resultsTbl,fldList[3:],whereClause)
for row in cursor:
    #write the species name + all the row data
    writer.writerow([speciesName] + list(row))

# Close file and clean up
csvFile.close()

## WRITE THE BACKGROUND FILE ##
msg("Writing the background file...")
# Initialize the species output csv file & create the writer object
msg("Initializing the output CSV files")
csvFile = open(backgroundCSV,'wb')
writer = csv.writer(csvFile, quoting=csv.QUOTE_NONNUMERIC)

# Write header row to CSV file
msg("Writing headers to CSV file")
writer.writerow(fldList)

# Create a search cursor for the inputTbl
msg("Writing values to CSV file")
whereClause = '"{}" <> 1'.format(speciesName)
cursor = arcpy.da.SearchCursor(resultsTbl,fldList[3:],whereClause)
for row in cursor:
    #write the species name + all the row data
    writer.writerow(['background'] + list(row)) 

# Close file and clean up
csvFile.close()

msg("Finished")