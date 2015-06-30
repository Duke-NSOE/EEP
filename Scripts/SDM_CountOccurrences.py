# SDM_CountOccurrences.py
#
# Description: Tallies the number of species found within a given HUC 6.
#  This can be used to identify species with minimum occurrence points
#  to run species distribution modeling. 
#
# John Fay
# Summer 2015

# Import modules
import sys,os,arcpy

# User variables
inTbl = arcpy.GetParameterAsText(0)
HUC6 = arcpy.GetParameterAsText(1)
freqTbl = arcpy.GetParameterAsText(2)

# script variables
sppTbl = ("in_memory/SppTbl")
whereClause = '[HUC_8] LIKE \'{}%\''.format(HUC6)

# Messaging function
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)

#Make a table of the Excel Worksheet"
msg("Selecting species records in HUC6 = {}".format(HUC6))
sppTbl = arcpy.TableSelect_analysis(inTbl,sppTbl,whereClause)
msg("...{} records selected".format(arcpy.GetCount_management(sppTbl).getOutput(0)))

#Tally the occurrences of each species within the given HUC using the Frequency Tool
msg("Tabulating counts for species in HUC6 {}".format(HUC6))
arcpy.Frequency_analysis(sppTbl,freqTbl,["CommonName","Scientific"])

msg("Finished")