# MAXENT_ResultsToBackground.py
#
# Description: Creates a MaxEnt input CSV file in SWD (species with data) format. Includes a
#  column listing the species/background along with columns for all the env vars. Inputs are
#  limited to only catchments with any species data. We could include all [non-surveyed]
#  catchments, but we need to exclude those where the species has been observed. 
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv
arcpy.env.overwriteOutput = True

# Input variables
speciesTbl = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Data\EEP_030501.gdb\HabModel'
# arcpy.GetParameterAsText(1) #NHD catchments tagged with species presence
## speciesTbl conists of all ENDRIES surveyed catchments with a binary column for each species presence...
resultsTbl = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Data\EEP_030501.gdb\results'

speciesName = "Nocomis_leptocephalus"
# arcpy.GetParameterAsText(3) #Species to model

# Output variables
speciesCSV = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\MaxEnt\ME_species.csv'
#arcpy.GetParameterAsText(3)    # MaxEnt species file

# Script varables
EnvVarCount = 107 ##<--Number of environment variables; after this it's species columns
sppOnlyTbl = "in_memory/SppTble"
resultsCopyTbl = "in_memory/Results2"
counter = 0

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
msg("Pulling catchment records for {}".format(speciesName))
arcpy.TableSelect_analysis(speciesTbl, sppOnlyTbl,'"{}" = 1'.format(speciesName))

# Make a copy of the environment variable table and join the species table to it
msg("...Creating temporary table of the environment variables")
arcpy.CopyRows_management(resultsTbl,resultsCopyTbl)

# Join the species data to the results table so that the records where the species
# is present can be isolated. 
msg("...Joining species presence values to environment variables")
arcpy.JoinField_management(resultsCopyTbl,"GRIDCODE",sppOnlyTbl,"GRIDCODE","{}".format(speciesName))

# Create a list of field names
msg("Generating a list of environment variables for processing") 
fldList = [] #[speciesName] #start the list with the MaxEnt format: {species name, x, y}
for fld in arcpy.ListFields(resultsCopyTbl)[:EnvVarCount]:
    fldList.append(str(fld.name))

## WRITE THE SPECIES RECORDS TO THE FILE ##
msg("Iniitializing the output species file...")
# Initialize the species output csv file & create the writer object
msg("...Initializing the output CSV files")
csvFile = open(speciesCSV,'wb')
writer = csv.writer(csvFile)#, quoting=csv.QUOTE_NONNUMERIC)

# Write header row to CSV file
msg("...Writing headers to CSV file")
writer.writerow(["Species","X","Y"] + fldList[3:])

# Create a search cursor for the resultsTbl
msg("...Writing presence values to CSV file")
whereClause = '"{}" = 1'.format(speciesName)
cursor = arcpy.da.SearchCursor(resultsCopyTbl,fldList[1:],whereClause)
for row in cursor:
    #write the species name + all the row data
    writer.writerow([speciesName] + list(row))
    counter += 1
msg("{} presence records writted to file".format(counter))
counter = 0

# Create a search cursor for the resultsTbl
msg("...Writing background values to CSV file")
whereClause = '"{}" IS Null'.format(speciesName)
cursor = arcpy.da.SearchCursor(resultsCopyTbl,fldList[1:],whereClause)
for row in cursor:
    #write the species name + all the row data
    writer.writerow(['background'] + list(row))
    counter +=1
msg("{} absence records writted to file".format(counter))

# Close file and clean up
csvFile.close()

msg("Finished")