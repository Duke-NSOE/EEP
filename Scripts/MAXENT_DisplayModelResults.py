# MAXENT_DisplayModelResults.py
#
# Merges Maxent result tables to the catchment feature class to display results
#
# Spring 2015
# John.Fay@duke.edu

import arcpy, sys, os, csv
arcpy.env.overwriteOutput = 1

# Input variables
CatchmentFC = arcpy.GetParameterAsText(0)  #r"C:\WorkSpace\EEP_Spring2015\EEP_Tool\Data\EEP_030501.gdb\EnvStats"
maxentFolder = arcpy.GetParameterAsText(1) #r"C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\Nocomis_leptocephalus\Output"

# Output
outFC = arcpy.GetParameterAsText(2) #r"C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\Nocomis_leptocephalus\HabModel.shp"

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
msg("Getting Maxent files...")
resultsFN = os.path.join(maxentFolder,"maxentResults.csv")
logisticFN = os.path.join(maxentFolder,sppName+".csv")
predictionFN = os.path.join(maxentFolder,sppName+"_samplePredictions.csv")

#Make sure the results exist
for f in (resultsFN, logisticFN, predictionFN):
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

#Create a table of from the logistic CSV
msg("Converting {} to a table".format(logisticFN))
logTbl = arcpy.CopyRows_management(logisticFN,"in_memory/Logistic")

#Get the logistic field name
msg("Getting list of habitat attributes used in model.")
logFld = arcpy.ListFields(logTbl)[-1].name

#Make a feature layer of the catchment features
msg("Creating a feature layer of catchment features")
fldInfo = arcpy.FieldInfo()
for f in arcpy.ListFields(CatchmentFC):
    fName = f.name
    if fName in ("OBJECTID","Shape","GRIDCODE","FeatureID"):
        fldInfo.addField(fName,fName,"VISIBLE","")
    else:
        fldInfo.addField(fName,fName,"HIDDEN","")
catchLyr = arcpy.MakeFeatureLayer_management(CatchmentFC,"catchLyr","","",fldInfo)

#Join the Maxent results to it
msg("Joining maxent results to catchment features")
arcpy.AddJoin_management(catchLyr,"GRIDCODE",logTbl,"X")

#Export the results
msg("Copying results to {}".format(outFC))
arcpy.Select_analysis(catchLyr, outFC,'"Logistic.X" > 0')

#Remove all but the first two and last four fields
msg("Cleaning up fields")
for fld in arcpy.ListFields(outFC)[2:-4]:
    arcpy.DeleteField_management(outFC, fld.name)

#Create and update output fields
msg("Adding habitat probability field...")
arcpy.AddField_management(outFC,"HabProb","DOUBLE")

msg("Updating habitat probability values...")
arcpy.CalculateField_management(outFC,"HabProb","[Logistic_E]")

msg("Adding habitat binary field...")
arcpy.AddField_management(outFC,"HabBinary","Short")

msg("Updating habitat binary values..")
arcpy.CalculateField_management(outFC,"HabBinary","!Logistic_E! > {}".format(threshold),"PYTHON")

#Remove fields
msg("Cleaning up.")
arcpy.DeleteField_management(outFC,["Logistic_O","Logistic_X","Logistic_Y","Logistic_E"])

