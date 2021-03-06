# MAXENT_CreateSWDFile.py
#
# Description: Creates a MaxEnt input CSV file in SWD (species with data) format. Includes a
#  column listing the species/background along with columns for all the env vars. Records produced
#  are limited to only catchments with recorded presences from any species in Endries' data.
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv
arcpy.env.overwriteOutput = True

# Input variables
speciesTbl = arcpy.GetParameterAsText(0) # table of all ENDRIES surveyed catchments with a binary column for each species presence...
speciesName = arcpy.GetParameterAsText(1) #Species to model; this should be a field in the above table
resultsTbl = arcpy.GetParameterAsText(2) # table listing all the catchment attributes to be used as environment layer values
varFilterCSV = arcpy.GetParameterAsText(3) #r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\Nocomis_leptocephalus\CorrelatedFields.csv'

# Output variables
speciesCSV = arcpy.GetParameterAsText(4) #Output SWD format CSV file to create

# Script varables
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
#arcpy.CopyRows_management(resultsTbl,resultsCopyTbl)
arcpy.TableSelect_analysis(resultsTbl,resultsCopyTbl,"LENGTHKM > 0")

# Remove uncorrelated fields
f = open(varFilterCSV,'rt')
keepList = ["OBJECTID","GRIDCODE","FEATUREID"]
for row in csv.reader(f):
    keepList.append(row[0])
f.close()
killList = []
fldList = arcpy.ListFields(resultsCopyTbl)
for fld in fldList:
    if not fld.name in keepList:
        msg("Removing {} from output".format(fld.name))
        arcpy.DeleteField_management(resultsCopyTbl,fld.name)
        

# Join the species data to the results table so that the records where the species
# is present can be isolated. 
msg("...Joining species presence values to environment variables")
arcpy.JoinField_management(resultsCopyTbl,"GRIDCODE",sppOnlyTbl,"GRIDCODE","{}".format(speciesName))

# Create a list of field names
msg("Generating a list of environment variables for processing") 
fldList = [] #[speciesName] #start the list with the MaxEnt format: {species name, x, y}
for fld in arcpy.ListFields(resultsCopyTbl):
    fldList.append(str(fld.name))

## WRITE THE SPECIES RECORDS TO THE FILE ##
msg("Iniitializing the output species file...")
# Initialize the species output csv file & create the writer object
msg("...Initializing the output CSV files")
csvFile = open(speciesCSV,'wb')
writer = csv.writer(csvFile)

# Write header row to CSV file
msg("...Writing headers to CSV file")
writer.writerow(["Species","X","Y"] + fldList[3:-1]) #<- the 3: is to skip the first three columns in the fldList

# Create a search cursor for the resultsTbl
msg("...Writing presence values to CSV file")
whereClause = '"{}" = 1'.format(speciesName)
# Create a cursor including all but the first and last fields (species names)
cursor = arcpy.da.SearchCursor(resultsCopyTbl,fldList[1:-1],whereClause) #<- the 1: skips the first & last field
for row in cursor:
    #write the species name + all the row data
    writer.writerow([speciesName] + list(row))
    counter += 1
msg("{} presence records writted to file".format(counter))
counter = 0

# Create a search cursor for the resultsTbl
msg("...Writing background values to CSV file")
whereClause = '"{}" IS Null'.format(speciesName)
cursor = arcpy.da.SearchCursor(resultsCopyTbl,fldList[1:-1],whereClause)
for row in cursor:
    #write the species name + all the row data
    writer.writerow(['background'] + list(row))
    counter +=1
msg("{} absence records writted to file".format(counter))

# Close file and clean up
csvFile.close()

msg("Finished")