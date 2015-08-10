# MAXENT_projectionASCIItoCSV.py
#
# Reverts the ASCII pseudo raster of model prediction back into CSV format so that it can 
#  be joined back to the catchment features used to run the model and ultimately mapped.
#
# The inputs include: (1) the projection ASCII file produced by running MaxEnt, (2) the MaxEnt
#  samples with data (SWD) CSV file, and the output CSV file that will include a field of the
#  catchment ID and the habitat likelihood.
#
# Note that the second field in the SWD file will be used as the joining field. 
#
# The ASCII projection file, after its 6-line header is simply a list of probabilities
#   corresponding to the NHD catchments listed in the input SWD file used to run MaxEnt
#
# Spring 2015
# John.Fay@duke.edu

import arcpy, sys, os, csv

# Input variables
prjFN = arcpy.GetParameterAsText(0) 
swdFN = arcpy.GetParameterAsText(1) 
outCSV = arcpy.GetParameterAsText(2)

# ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)

# ---Processes---
#Create a list of the FEATUREIDs from the swd file
msg("Creating a list of Feature IDs from the MaxEnt SWD file")
featureIDs = []
file = open(swdFN,'r')
reader = csv.reader(file)
for row in reader:
    featureIDs.append(row[1])
file.close()
featCount = len(featureIDs)
msg("{} features to be processed".format(featCount))

#Create a list of MaxEnt Likelihoods from the projection ASCII file         
msg("Creating a list of habitat probabilities from the MaxEnt SWD file")
valueIDs = ["HabProb"]
file = open(prjFN,'r')
reader = csv.reader(file,delimiter=" ")
## Skip the ASCII header rows
for row in reader:
    if not row[0] in ('ncols','nrows','xllcorner','yllcorner','cellsize','NODATA_value'):
        #Replace NoData with zeros
        if row[0] == '-9999': habProb = 0
        #Write out scientific notation
        elif "E-" in row[0]:
            #val,expt = row[0].split["E"]
            habProb = str(float(row[0]))
        else: habProb = row[0]
        #write the value to the list
        valueIDs.append(habProb)    
file.close()
valCount = len(valueIDs)

#Write the lists to the output file
file = open(outCSV,'wb')
writer = csv.writer(file)
## Write the header line
writer.writerow(("GRIDCODE", "HabProb"))
for i in range(2,len(featureIDs)):
    writer.writerow((featureIDs[i-1],valueIDs[i-1]))
file.close()

#Merge with 