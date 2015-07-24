# STATS_MergeCoeffTables.py
#
# Description:
#  Merges coefficient tables for multiple species into a single table
#
# Summer 2015
# John.Fay@duke.edu

import sys, os, arcpy, csv
arcpy.env.overwriteOutput = 1

# Input variables
#inputFiles = arcpy.GetParameterAsText(0)
#responseVarsFC = arcpy.GetParameterAsText(1)
arcpy.env.workspace = os.path.abspath(os.path.dirname(sys.path[0]) + "\\Maxent")
inputFiles = arcpy.ListFiles("*.csv")
responseVarsFC = r'C:\WorkSpace\EEP_Tool\Data\EEP_030501.gdb\ResponseVars'
# Output variables
outputCSV = r"C:\WorkSpace\EEP_Tool\scratch\tmp.csv"
outputTbl = r"C:\WorkSpace\EEP_Tool\MaxEnt\Santee.gdb\SanteeSpp"

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
    if fld.name not in ("OBJECTID","SHAPE","GRIDCODE","FEATUREID","SCOURCEFC","Shape_Length","Shape_Area","FTYPE","REACHCODE"):
        fldList.append(str(fld.name))

#Create the output csv
file = open(outputCSV,'wb')
writer = csv.writer(file)
writer.writerow(["variable"])
for f in fldList:
    writer.writerow([f])
file.close()

#Convert csv to table
msg("Converting csv to table")
arcpy.CopyRows_management(outputCSV,outputTbl)

msg("Removing csv")
os.remove(outputCSV)

#Add total field
msg("Adding total field")
arcpy.AddField_management(outputTbl,"Total","SHORT")

#Make sppName list
sppNameList = []

#Merge tables
for spp in inputFiles:
    genus,species = spp.split("_")
    sppName = str(genus[0].capitalize() + "_" + species[:-4])
    sppNameList.append(sppName)
    msg("Joining {}".format(sppName))
    flds = "{0}_c;{0}_p;{0}_keep".format(sppName)
    db = arcpy.CopyRows_management(spp,r"C:\WorkSpace\EEP_Tool\MaxEnt\Santee.gdb\{}".format(sppName))
    arcpy.JoinField_management(outputTbl,"variable",db,"variable", flds)

#Create calc string
msg("Creating calculation string")
calcString = ""
for spp in sppNameList:
    calcString += "[{}_keep]+".format(spp)

#Calculate totals
msg("Calculating totals")
arcpy.CalculateField_management(outputTbl,"Total",calcString[:-1])

msg("Finished")


