# MAXENT_ExtractVariableImportance.py
#
# Description: Extracts the variable importance values from MaxEnt results 
#    and creates a CSV table.
#
# Inputs: Maxent output folder (must contain the maxentResults.csv file)
#
# Outputs: A table listing the modeled response variables and for each their:
#  - Percent Contribution
#  - Permutation Importance
#  - Gain without the variable
#  - Gain with only the variable
#
# Spring 2015
# John.Fay@duke.edu

import arcpy, sys, os, csv
arcpy.env.overwriteOutput = 1

# Input variables
maxentFolder = arcpy.GetParameterAsText(0)

# Output
outFC = arcpy.GetParameterAsText(1)  

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
sppLine = lines[11]
sppName = sppLine[9:-1]

#Get the result filenames
msg("...Locating Maxent result file...")
resultsFN = os.path.join(maxentFolder,"maxentResults.csv")
if not os.path.exists(resultsFN):
    msg("File {} does not exist.\nExiting.".format(f),"error")
    sys.exit()

#Read in the data from the maxent result file
msg("...Extracting data from maxent result file")
f = open(resultsFN,'rt')
reader = csv.reader(f)
row1 = reader.next()
row2 = reader.next()
f.close()

#Make dictionaries for the 4 metrics
contribDict = {}
permDict = {}
withoutDict = {}
withDict = {}

#Loop throught items in row1
msg("...extracting data from maxent.csv file")
for item in row1:
    #Add data items to the respective dictionary if the header contains it
    if "contribution" in item:
        idx = row1.index(item)
        key = item[:-13] #Just get the variable name
        val = row2[idx]
        contribDict[key] = val
    elif "permutation" in item:
        idx = row1.index(item)
        key = item[:-23]
        val = row2[idx]
        permDict[key] = val
    elif "gain without" in item:
        idx = row1.index(item)
        key = item[22:]
        val = row2[idx]
        withoutDict[key] = val
    elif "gain with" in item:
        idx = row1.index(item)
        key = item[24:]
        val = row2[idx]
        withDict[key] = val

#Initialize the output table
msg("...initializing output file")
f = open(outFC,'wb')
w = csv.writer(f)
w.writerow(("Variable","Contribution","PermImportance","GainWithout","GainWithonly"))

#Check to see that > 1 variable was used, exit if not
if len(contribDict.keys()) <= 1:
    msg("Only 1 variable in model","warning")
    w.writerow((key,contribDict[key],permDict[key],0,0))
    f.close()
    sys.exit(0)

#Write dictionary values to the csv file
msg("...writing variables to output file")
for key in contribDict.keys():
    dataList = (key,contribDict[key],permDict[key],withoutDict[key],withDict[key])
    w.writerow(dataList)

f.close()
