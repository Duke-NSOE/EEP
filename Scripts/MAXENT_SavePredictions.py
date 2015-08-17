# MAXENT_SavePredictions.py
#
# Saves Maxent raw logistical and thresholded output to csv
#
# Spring 2015
# John.Fay@duke.edu

import arcpy, sys, os, csv
arcpy.env.overwriteOutput = 1

# Input variables
maxentFolder = arcpy.GetParameterAsText(0)

# Output
outCSV = arcpy.GetParameterAsText(1) 

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
## Get the MaxEnt result files
#Get the species name from the maxent log file
logFN = os.path.join(maxentFolder,"maxent.log")
if not os.path.exists(logFN):
    msg("File {} does not exist.\nExiting.".format(logFN),"error")
    sys.exit()
f = open(logFN,"r")
lines = f.readlines()
f.close()

#Get the species name
sppName = "Unknown"
for line in lines:
    if line[:9] == "Species: ": sppName = line[9:-1]

#Get the result filenames
msg("Getting Maxent files...")
resultsFN = os.path.join(maxentFolder,"maxentResults.csv")
logisticFN = os.path.join(maxentFolder,sppName+".csv")

#Make sure the result files exist
for f in (resultsFN, logisticFN):
    if not os.path.exists(f):
        msg("File {} does not exist.\nExiting.".format(f),"error")
        sys.exit()

#Get the threshold (column 255 in the maxentResults.csv)
f = open(resultsFN,'rt')
reader = csv.reader(f)
row1 = reader.next()
row2 = reader.next()
f.close()
idx = row1.index('Balance training omission, predicted area and threshold value logistic threshold')
threshold = row2[idx]
msg("Maxent logistic threshold set to {}".format(threshold))

# Read in the predictions; make a list of values
msg("reading in logistic values")
predList = []
f = open(logisticFN,'rt')
row1 = f.readline()
row2 = f.readline()
while row2:
    predList.append(row2.split(","))
    row2 = f.readline()
f.close()
    
# Write the output to a file
msg("Creating Maxent Output File")
f = open(outCSV,'w')
f.write("GRIDCODE,PROB,HABITAT\n")
for rec in predList:
    gridcode = rec[0]
    prob = float(rec[2])
    if prob >= float(threshold): hab = 1
    else: hab = 0
    f.write("{},{},{}\n".format(gridcode,prob,hab))
f.close()

