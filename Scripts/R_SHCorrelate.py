# R_SHCorrelate.py
#
# Description:
#  Correlate spp presence/absence with habitat variables. 
#
# Spring 2015
# John.Fay@duke.edu

#from setuptools.command import easy_install
#easy_install.main(["-U","scipy"])

import sys, os, csv, arcpy, numpy
arcpy.env.overwriteOutput = 1

'''DEBUG INPUTS
C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\E_complanata2.csv
'''

# Input variables
speciesCSV = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\E_complanata2.csv'#arcpy.GetParameterAsText(0)

# Output variables

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
#Read in the column headers
f = open(speciesCSV,'rt')
headerText = f.readline()
headerItems = headerText.split(",")
f.close()

#Read in the csv file as a numpy vector
msg("Reading in data from {}".format(speciesCSV))
arrData = numpy.genfromtxt(speciesCSV,delimiter=",")

#Create variables from data array
nCols = arrData.shape[1]

#Create vectors
msg("Extracting occurrence records")
sppVector = arrData[1:,0]

i = 1 #Replace with loop
for i in range(nCols):
    envName = headerItems[i]
    envVector = arrData[1:,i]

    #Calculate correlation
    pearson = numpy.corrcoef(sppVector,envVector)[0,1]
    #Print output
    msg("{}\t{}".format(envName,pearson))

    if i > 1: break
