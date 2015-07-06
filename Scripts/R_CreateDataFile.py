# R_CreateDataFile.py
#
# Description: Creates a CSV format table listing all the catchments in each HUC8 in which a
#   selected species is found. The table includes a column indicating whether the species was
#   observed in the catchment and all environment environment data. Any environment layer with
#   missing data is omitted completely. 
#
# The procedure first finds all the HUC8s in which the species occurs, then
#   extracts all the catchments within these HUC8s. Those catchments where the
#   species was observed (via Endries' data) are tagged with 1, others with 0.bit_length
#   Environment variables with missing data are eliminated. 
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, csv, arcpy
arcpy.env.overwriteOutput = 1

# Input variables
speciesTbl = arcpy.GetParameterAsText(0)    # Table of all ENDRIES surveyed catchments with a binary column for each species presence...
speciesName = arcpy.GetParameterAsText(1)   # Species to model; this should be a field in the above table
envVarsTbl = arcpy.GetParameterAsText(2)    # Table listing all the catchment attributes to be used as environment layer values

# Output variables
speciesCSV = arcpy.GetParameterAsText(3)    # CSV file listing the species occurence and all env vars for HUC8s in which species occurs

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
# Trim of the last "OR "
whereClause = whereClause[:-3]

# Select the records
# Make a copy of the environment variable table and join the species table to it
msg("...Creating temporary table of the environment variables")
arcpy.TableSelect_analysis(envVarsTbl,resultsCopyTbl,whereClause)

# Join the species data to the results table so that the records where the species
# is present can be isolated. 
msg("...Joining species presence values to environment variables")
arcpy.JoinField_management(resultsCopyTbl,"GRIDCODE",sppOnlyTbl,"GRIDCODE","{}".format(speciesName))

# Create a list of field names: remove non-numeric fields and extranneous fields
outFldList = []
for fld in arcpy.ListFields(resultsCopyTbl):
    if fld.type in ("Double","Integer","SmallInteger") and \
       not fld.name in ("GRIDCODE","FEATUREID",speciesName):
        outFldList.append(fld.name)
# Remove the first two and the last fields
outFldList = outFldList[1:-1]

# Filter the field list: remove fields with null values
fldList = []
for fld in outFldList:
    #Create the SQL filter
    sql = "{} IN (-9998.0,-9999)".format(fld)
    #Select records
    tmpTbl = arcpy.TableSelect_analysis(resultsCopyTbl,"in_memory/tmpSelect",sql)
    #See if any records are selected
    if int(arcpy.GetCount_management(tmpTbl).getOutput(0)) == 0:
        fldList.append(fld)
    else:
        msg("   Field <<{}>> has null values and will be removed".format(fld),"warning")

## WRITE THE SPECIES RECORDS TO THE FILE ##
msg("Creating the output species file...")
# Initialize the species output csv file & create the writer object
msg("...Initializing the output CSV files")
csvFile = open(speciesCSV,'wb')
writer = csv.writer(csvFile)

# Write header row to CSV file
msg("...Writing headers to CSV file")
writer.writerow(["Species"] + fldList)

# Create a search cursor for the resultsTbl
msg("...Writing presence values to CSV file")
whereClause = '"{}" = 1'.format(speciesName)
# Create a cursor including all but the first and last fields (species names)
cursor = arcpy.da.SearchCursor(resultsCopyTbl,fldList,whereClause) #<- the 1: skips the first & last field
for row in cursor:
    #write the species name + all the row data
    writer.writerow([1] + list(row))
    counter += 1
msg("{} presence records writted to file".format(counter))
counter = 0

# Create a search cursor for the resultsTbl
msg("...Writing background values to CSV file")
whereClause = '"{}" IS Null'.format(speciesName)
cursor = arcpy.da.SearchCursor(resultsCopyTbl,fldList,whereClause)
for row in cursor:
    #write the species name + all the row data
    writer.writerow([0] + list(row))
    counter +=1
msg("{} absence records writted to file".format(counter))

# Close file and clean up
csvFile.close()

msg("Finished")
