# STATS_CalculateOccurrenceCorrelation.py
#
# Description:
#  Correlate spp presence/absence with habitat variables.
#
#  *****************************************************************************
#  ** This module requires the SciPy module to be installed. When installing, **
#  ** be sure to get version 0.12.0 as that is the one that works with the    **
#  ** version of NumPy that is installed with ArcGIS 10.2                     ** 
#  *****************************************************************************
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy, numpy
arcpy.env.overwriteOutput = 1

# Input variables
speciesCSV = arcpy.GetParameterAsText(0)
speciesName = arcpy.GetParameterAsText(1)

# Output variables
correlationCSV = arcpy.GetParameterAsText(2)

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
#Check to see whether a SciPy exists
try:
    import scipy
    from scipy import stats
except:
    msg("The SciPy module is not installed.\nExiting.","error")
    sys.exit()

#Abbreviate species name
genus,species = speciesName.split("_")
sppName = (genus[0]+"_"+species).capitalize()
    
#Read in the column headers
f = open(speciesCSV,'rt')
headerText = f.readline()
headerText = headerText[:-1] #Strip the newline char
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

#Intialize output file
msg("Creating output file {}".format(correlationCSV))
f = open(correlationCSV,'wt')
f.write("variable, {}_c, {}_p, {}_keep\n".format(sppName,sppName,sppName))
#f.write("variable, coef, p, keep\n".format(sppName,sppName,sppName))

#Loop through columns and calculate the variables correlation with presence/absence
msg("Calculating correlation coefficients")
for i in range(1,nCols):
    # Get the variable name (from the list created above)
    envName = headerItems[i]
    # Skip if name is GRIDCODE or FeatureID
    if envName in ("GRIDCODE","FeatureID","REACHCODE"): continue
    # Get the env var column, as a vector
    envVector = arrData[1:,i]
    #Calculate correlation --THIS REQUIRES SCIPY--
    pearson = stats.pearsonr(sppVector, envVector)
    coeff = pearson[0]
    pValue = pearson[1]
    #Print output to the CSV file
    if abs(pValue) <= 0.05:
        f.write("%s, %2.4f, %2.3f, %s\n"%(envName,coeff,pValue,1))
    else:
        f.write("%s, %2.4f, %2.3f, %s\n"%(envName,coeff,pValue,0))

#Wrap up
f.close()
msg("Finished")               

