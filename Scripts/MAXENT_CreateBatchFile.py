# MAXENT_CreateBatchFile.py
#
# Creates a batch file (.bat) used to run MaxEnt with the supplied files
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy

# Path variables
dataPth = os.path.abspath(sys.path[0]+ "\\..\\Scratch")

# Input variables
sppFile = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\species.csv'
csvFile = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\EnvVars.csv'
species = 'Nocomis_leptocephalus'
whereClause = ''

# Output variables
maxentFile = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\Maxent.bat'

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
dict = {}
dict["outputdirectory"] = dataPth
dict["samplesfile"] = sppFile
dict["environmentallayers"] = csvFile

# Fields to turn off
offFlds = ("Shape_Length",
           "Shape_Area",
           "REACHCODE",
           "FCODE",
           "QLOSS0001",
           "AreaSqKM_1",
           "FEATUREID_1",
           "Other",
           "Forest",
           "Wetland",
           "TotLength")

# Categorical fields
catFlds = ("FTYPE",
           "StreamOrde")

# Boilerplate
runString = "java -mx2048m -jar maxent.jar "

# Add dictionary items
for key,value in dict.items():
    runString = runString +  " {}={}".format(key, value)

# Turn fields off
for offFld in offFlds:
    runString = runString + " togglelayerselected={}".format(offFld)

# Set categorical fields
for catFld in catFlds:
    runString = runString + "  togglelayertype={}".format(catFld)
outFile = open(maxentFile,'w')
outFile.write(runString)
outFile.close()