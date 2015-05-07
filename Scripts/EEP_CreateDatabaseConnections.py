#EEP_CreateDatabaseConnections.py
#
# Description: Creates a set of connections to SDE databases used for extracting data
#
# May 2015
# John.Fay@duke.edu

import sys, os, arcpy

#Set path variables
dataPath = dataPth = os.path.abspath(sys.path[0]+ "\\..\\Data")

#Input variables
userName = arcpy.GetParameterAsText(0) #"NHDread"
userPwd = arcpy.GetParameterAsText(1)

#Script variables
databases = [["NHDPlusV2","NHD data.sde"],["USdata","NLCD data.sde"],["NC","NC.sde"]]

for db, sdeName in databases:
    print "Creating connection file for {}".format(db)
    arcpy.CreateDatabaseConnection_management(out_folder_path=dataPath,
                                              out_name=sdeName,
                                              database_platform="SQL_SERVER",
                                              instance="ns-gis.win.duke.edu, 5151",
                                              account_authentication="DATABASE_AUTH",
                                              username=userName,
                                              password=userPwd,
                                              save_user_pass="SAVE_USERNAME",
                                              database=db)


