#Util_ExportDatabase.py
#
# Description: Exports the DMS SDE Databases to an XML document
#
# July 2015
# John.Fay@duke.edu

import sys, os, arcpy, time

#Script variables
rootPath = os.path.abspath(os.path.join(sys.path[-1],".."))
dataPath = os.path.join(rootPath,"Data")
ncSDE = os.path.join(dataPath,"NC.sde")
nhdSDE = os.path.join(dataPath,"NHD data.sde")
nlcdSDE = os.path.join(dataPath,"NLCD data.sde")

xmlPath = "C:/temp/XMLs"
ncXML = os.path.join(xmlPath,"NC.xml")
#ncXML = os.path.join(xmlPath,"NC.zip")

print "Converting NC SDE to (zipped) XML"
arcpy.ExportXMLWorkspaceDocument_management(ncSDE, ncXML,"DATA","BINARY","METADATA")

