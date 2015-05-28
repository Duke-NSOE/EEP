# R_CreateDataFile.py
#
# Description: Creates the files necessary to run R analyses.These include:
#  - Presences file
#  - Available habitat file
#
# The procedure first finds all the HUC8s in which the species occurs, then
#   extracts all the catchments within these HUC8s. Those catchments where the
#   species was observed (via Endries' data) are tagged with 1, others with 0
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, csv, arcpy
arcpy.env.overwriteOutput = 1

'''DEBUG INPUTS
C:\WorkSpace\EEP_Spring2015\EEP_Tool\Data\EEP_030201.gdb\HabModel Elliptio_complanata C:\WorkSpace\EEP_Spring2015\EEP_Tool\Data\EEP_030201.gdb\EnvStats C:\WorkSpace\EEP_Spring2015\EEP_Tool\Data\foo.csv
'''

# Input variables
speciesTbl = arcpy.GetParameterAsText(0) # table of all ENDRIES surveyed catchments with a binary column for each species presence...
speciesName = arcpy.GetParameterAsText(1) #Species to model; this should be a field in the above table
envVarsTbl = arcpy.GetParameterAsText(2) # table listing all the catchment attributes to be used as environment layer values

# Output variables
speciesCSV = arcpy.GetParameterAsText(3)

# Script variables
sppOnlyTbl = "in_memory/sppOnlyTbl"
freqTbl = "in_memory/FreqTbl"
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

# Make a list of HUC8s
msg("Making a list of HUC8s in which {} was observed".format(speciesName))
msg("...Joining fields")
arcpy.JoinField_management(sppOnlyTbl,"GRIDCODE",envVarsTbl,"GRIDCODE","REACHCODE")
msg("...Determining HUC8s from REACHCODE attribute")
HUC8s = []
for rec in arcpy.da.SearchCursor(sppOnlyTbl,("REACHCODE")):
    HUC8 = str(rec[0][:8])
    if not HUC8 in HUC8s:
        HUC8s.append(HUC8)
msg("{} was found in {} HUC8s".format(speciesName,len(HUC8s)))
# Drop the REACHCODE field
arcpy.DeleteField_management(sppOnlyTbl,"REACHCODE")

# Select data rows that are within the specified HUC8s
# Create a where clause from the HUC8s
msg("Creating the query string to extract records")
whereClause = ""
for HUC8 in HUC8s:
    whereClause += "REACHCODE LIKE '{}%' OR ".format(HUC8)
# Trim of the last or
whereClause = whereClause[:-3]
print whereClause

# Select the records
# Make a copy of the environment variable table and join the species table to it
msg("...Creating temporary table of the environment variables")
arcpy.TableSelect_analysis(envVarsTbl,resultsCopyTbl,whereClause)

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
writer.writerow(["Species"] + fldList[1:-1]) #skip the first and last columns in the fldList

# Create a search cursor for the resultsTbl
msg("...Writing presence values to CSV file")
whereClause = '"{}" = 1'.format(speciesName)
# Create a cursor including all but the first and last fields (species names)
cursor = arcpy.da.SearchCursor(resultsCopyTbl,fldList[1:-1],whereClause) #<- the 1: skips the first & last field
for row in cursor:
    #write the species name + all the row data
    writer.writerow([1] + list(row))
    counter += 1
msg("{} presence records writted to file".format(counter))
counter = 0

# Create a search cursor for the resultsTbl
msg("...Writing background values to CSV file")
whereClause = '"{}" IS Null'.format(speciesName)
cursor = arcpy.da.SearchCursor(resultsCopyTbl,fldList[1:-1],whereClause)
for row in cursor:
    #write the species name + all the row data
    writer.writerow([0] + list(row))
    counter +=1
msg("{} absence records writted to file".format(counter))

# Close file and clean up
csvFile.close()

msg("Finished")
