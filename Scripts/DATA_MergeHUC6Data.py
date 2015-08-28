# DATA_MergeHUC6Data.py
#
# Merges all the response var feature classes from the HUC6 geodatabases into a single
#  feature class and also makes a CSV file
#
# Fall 2015
# John.Fay@duke.edu

import sys, os, arcpy
arcpy.CheckOutExtension("spatial")

# Path variables
dataPth = os.path.abspath(sys.path[0]+ "\\..\\Data")

# Program variables
outCSV = r"C:\Workspace\EEP\Scratch\AllData.csv"

# Input variables


# Environment variables
arcpy.env.overwriteOutput = True


# ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)

# ---Procedures---
#Get a list of the HUC6 GDBs
arcpy.env.workspace = dataPth
gdbs = arcpy.ListWorkspaces("EEP_*")

#Create a list of fields from the first responsevars feature class
rvFC = os.path.join(gdbs[0],"ResponseVars")
flds = []
for fld in arcpy.ListFields(rvFC):
    if not (fld.name in {"OBJECTID","Shape"}):
        flds.append(str(fld.name))

#Initialize the output CSV
file = open(outCSV,'w')
#Make a string of the field name list (remove parentheses)
headers = str(flds)[1:-1]
#Remove single quotes
headers = headers.replace("'","")
#Write the field names
file.write("{}\n".format(headers))

#Loop through the response vars feature classes and write records
for gdb in gdbs:
    #Get the HUC6 from the path
    HUC6 = gdb[-10:-4]

    #Create the response var feature class variable
    rvFC = os.path.join(gdb,"ResponseVars")
    
    #Get the number of records
    numRecs = arcpy.GetCount_management(rvFC).getOutput(0)

    #Write the records to the CSV file
    msg("...processing {} records in {}".format(numRecs,HUC6))
    recs = arcpy.da.SearchCursor(rvFC,flds)
    for rec in recs:
        #Conver the values list to a string and chop the parentheses
        recString = str(rec)[1:-1]
        #Write the values to the CSV
        file.write("{}\n".format(recString))
    
    #Delete the cursor
    del recs

#Close the file
file.close()