# MAXENT_CreateBatchFile.py
#
# Creates a batch file (.bat) used to run MaxEnt with the supplied files
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, arcpy

# Path variables
maxentPath = os.path.abspath(sys.path[0]+ "\\..\\Maxent")

# Input variables
sppFile = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Maxent\ME_species.csv'
csvFile = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Maxent\ME_species.csv'
species = 'Nocomis_leptocephalus'

# Output variables
maxentFile = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\MaxEnt\{}.bat'.format(species)

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
dict["outputdirectory"] = maxentPath + "\\Output"
dict["samplesfile"] = sppFile
dict["environmentallayers"] = csvFile
dict["responsecurves"] = "true"
dict["jackknife"] = "true"
dict["togglespeciesselected"] = "background"

# Fields to turn off
offFlds = ("SOURCEFC",
           "Shape_Length",
           "Shape_Area",
           "REACHCODE",
           "FTYPE",
           "QLOSS0001",
           "Other",
           "Forest",
           "Wetland")

# Categorical fields
catFlds = ("FCODE",
           "StreamOrde")

# Boilerplate
runString = "java -mx2048m -jar maxent.jar"

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