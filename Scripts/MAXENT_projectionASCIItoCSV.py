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
prjFN = arcpy.GetParameterAsText(0) #r"C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scripts\RScripts\output\greenhead.shiner_PRJFiles.asc"
swdFN = arcpy.GetParameterAsText(1) #r"C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scripts\RScripts\greenhead_shiner_mxdata.csv"
outCSV = arcpy.GetParameterAsText(2)#r"C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scripts\RScripts\output\greenhead_shiner_projection.csv"

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

#Create a list of MaxEnt Likelihoods from the projection ASCII file         
msg("Creating a list of habitat probabilities from the MaxEnt SWD file")
valueIDs = ["HabProb"]
file = open(prjFN,'r')
reader = csv.reader(file)
for row in reader:
    if row[0][0].isdigit():
        valueIDs.append(row[0])
file.close()

#Write the lists to the output file
file = open(outCSV,'wb')
writer = csv.writer(file)
for i in range(1,len(featureIDs)):
    writer.writerow((featureIDs[i-1],valueIDs[i-1]))
file.close()