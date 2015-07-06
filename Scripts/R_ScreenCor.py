# R_ScreenCor.py
#
# Description: This script is used to identify which env variables are redundant.
#  It reads in the full data file for a species and a second file listing the
#  environment variable names to include (i.e. those found to correlate with
#  presence/absence) and computes pairwise correlation coefficients for all variables,
#  producing a table of variable pairs and their coefficients.  
#
# Spring 2015
# John.Fay@duke.edu

#from setuptools.command import easy_install
#easy_install.main(["-U","scipy"])

import sys, os, csv, arcpy, numpy
arcpy.env.overwriteOutput = 1

'''DEBUG INPUTS
C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\E_complanata2.csv C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\E_complanata2_shcX.csv 0.7 C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\E_complanata2_coeff.csv
'''

# Input variables
speciesCSV = arcpy.GetParameterAsText(0)
fieldsCSV = arcpy.GetParameterAsText(1)
threshold = arcpy.GetParameterAsText(2)

# Output variables
coeffCSV = arcpy.GetParameterAsText(3)

# Script variables

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
#Read in columns to process
msg("Reading in field names to include from {}".format(fieldsCSV))
colNames = []               # Create an empty list to add field names to 
f = open(fieldsCSV,'rt')    # Open the csv file
line = f.readline()         # Skip the header line
line = f.readline()         # Get the first data line
while line:                 # Loop through the remaining lines
    lineData = f.readline().split(",")  # Get the string in the line and split it into a list
    if len(lineData) > 1:               # If the line includes field names (the last one may not)
        colName = lineData[0]                      # Get the column name (first item)
        colName = colName.replace('"','')          # Remove any quotes
        colNames.append(colName)                   # Add the column name to the list 
    line = f.readline()                 # Go to the next line in the CSV file
f.close()                   # Close the file
#colNames.remove("TEMP0001")
msg("{} columns to analyze".format(len(colNames)))

#Read in all the column header names (from the full data file)
msg("Reading in column header names from {}".format(speciesCSV))
f = open(speciesCSV,'rt')
headerText = f.readline()
headerItems = headerText.split(",")
f.close()

#Read in the csv file as a numpy vector
msg("Reading in data from {}".format(speciesCSV))
arrData = numpy.genfromtxt(speciesCSV,delimiter=",")

#Create variables from data array
nCols = arrData.shape[1]

#Create the output CSV file
f = open(coeffCSV,'wt')
f.write("Var1, Var2, Coeff\n")

#Loop through column pairs
msg("Computing correlation values")
for i in range(0,nCols):
    for j in range(0,nCols):
        if j > i:
            # Get the names of the two columns
            name1 = headerItems[i]
            name2 = headerItems[j]
            # Process only if both the columns are in the colNames list (and the pairs aren't the same)
            if name1 in colNames and name2 in colNames and not (name1 == name2):
                # Get the data vectors of the two columns
                v1 = arrData[1:,i]
                v2 = arrData[1:,j]
                # Calculate the correlation coefficient
                pearson = numpy.corrcoef(v1,v2)[0,1]
                # If the coefficient is > the threshold consider them redundant and add to the CSV
                if abs(pearson) >= float(threshold):
                    f.write("{}, {}, {}\n".format(str(name1),name2,pearson))
                    #msg("{},{},{}".format(name1,name2,pearson))

msg("Values written to {}".format(coeffCSV))
f.close()
msg("Finished")

