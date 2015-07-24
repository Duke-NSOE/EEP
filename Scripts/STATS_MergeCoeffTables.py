# STATS_MergeCoeffTables.py
#
# Description:
#  Merges coefficient tables for multiple species into a single table
#
# Summer 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv, tempfile
arcpy.env.overwriteOutput = 1

# Input variables
inputFiles = arcpy.GetParameterAsText(0).split(";")
responseVarsFC = arcpy.GetParameterAsText(1)
#arcpy.env.workspace = os.path.abspath(os.path.dirname(sys.path[0]) + "\\Maxent")
#inputFiles = arcpy.ListFiles("*.csv")
#responseVarsFC = r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\ResponseVars'
# Output variables
outputTbl = arcpy.GetParameterAsText(2)#r"C:\WorkSpace\EEP_Tool\MaxEnt\Santee.gdb\SanteeSpp"

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
#Create a list of species from the inputs
speciesCSVs = inputFiles#.split(";")

#Create a list of response fields; these will be rows in the output
fldList = []
for fld in arcpy.ListFields(responseVarsFC):
    if fld.name not in ("OBJECTID","Shape","GRIDCODE","FEATUREID","SOURCEFC","Shape_Length","Shape_Area","FTYPE","REACHCODE"):
        fldList.append(str(fld.name))

#Create the output csv
tempCSV = tempfile.NamedTemporaryFile(suffix=".csv").name
file = open(tempCSV,'wb')
writer = csv.writer(file)
writer.writerow(["variable"])
for f in fldList:
    writer.writerow([f])
file.close()

#Convert csv to table
msg("Converting csv to table")
arcpy.CopyRows_management(tempCSV,outputTbl)

msg("Removing csv")
os.remove(tempCSV)

#Add total field
msg("Adding total field")
arcpy.AddField_management(outputTbl,"Total","SHORT")

#Make sppName list
msg("Initializing species list")
sppNameList = []

#Merge tables
for inputFile in inputFiles:
    #Get the filename
    spp = os.path.basename(inputFile)
    #Split into genus and species
    genus,species = spp.split("_")
    #Create an abbreviated name
    sppName = str(genus[0].capitalize() + "_" + species[:-4])
    #Add the abbreviated name to the sppName List (for calculating totals later)
    sppNameList.append(sppName)
    msg("...Joining {} to output table".format(sppName))
    #Need to convert the CSV to a table in order to join
    db = arcpy.CopyRows_management(spp,r"C:\WorkSpace\EEP_Tool\MaxEnt\Santee.gdb\{}".format(sppName))
    #Join the 3 fields together (can omit coefficient (c) and probability (p) if desired)
    #flds = "{0}_c;{0}_p;{0}_keep".format(sppName)
    flds = "{0}_keep".format(sppName)
    #Join..
    arcpy.JoinField_management(outputTbl,"variable",db,"variable", flds)

#Create calc string
msg("Creating calculation string to compute totals")
calcString = ""
for spp in sppNameList:
    calcString += "[{}_keep]+".format(spp)

#Calculate totals
msg("Calculating totals")
arcpy.CalculateField_management(outputTbl,"Total",calcString[:-1])

msg("Finished")


