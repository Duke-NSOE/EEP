# MAXENT_ExtractVariableImportance.py
#
# Extracts the variable importance values from MaxEnt results and creates a CSV table
#
# Spring 2015
# John.Fay@duke.edu

import arcpy, sys, os, csv
arcpy.env.overwriteOutput = 1

# Input variables
maxentFolder = arcpy.GetParameterAsText(0)  #r"C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\Nocomis_leptocephalus\Output"

# Output
outFC = arcpy.GetParameterAsText(1)  #r"C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\Nocomis_leptocephalus\VariableImportance.csv"

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
msg("Locating Maxent result file...")
resultsFN = os.path.join(maxentFolder,"maxentResults.csv")
if not os.path.exists(resultsFN):
    msg("File {} does not exist.\nExiting.".format(f),"error")
    sys.exit()

#Read in the data from the maxent result file
msg("Extracting data from {}".format(resultsFN))
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
msg("Writing output to {}".format(outFC))
f = open(outFC,'wb')
w = csv.writer(f)
w.writerow(("Variable","Contribution","PermImportance"))#,"GainWithout","GainWithonly"))

#Write dictionary values to the csv file
for key in contribDict.keys():
    dataList = (key,contribDict[key],permDict[key])#,withoutDict[key],withDict[key])
    w.writerow(dataList)

f.close()
msg("Finished")