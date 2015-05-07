#----------------------------------------------------------------------------------------
#PrepData.py
#
# Description: Extracts data for a user provided NHD HUC6 for stream habitat assessment
#
# Dec 2014
# John.Fay@duke.edu
#----------------------------------------------------------------------------------------

import sys, os, arcpy
import urllib as URLLIB
import urllib2 as URLLIB2
import json as JSON

arcpy.env.overwriteOutput = 1

#Inputs
HUC6 = '030201'
Flowlines = r'C:\WorkSpace\EEP_TarPam17Dec\Scratch\flowlines.shp'

#Misc functions
def msg(str,severity=""):
    print str
    if severity == "warning": arcpy.AddWarning(str)
    elif severity == "error": arcpy.AddError(str)
    else: arcpy.AddMessage(str)
    return
'''
    http://landscape1.arcgis.com/arcgis/rest/services/USA_NHDPlusV2/MapServer/3/query?
    where=reachcode+LIKE+%27030201*%27
    &text=
    &objectIds=
    &time=
    &geometry=
    &geometryType=esriGeometryPolyline
    &inSR=
    &spatialRel=esriSpatialRelIntersects
    &relationParam=
    &outFields=*
    &returnGeometry=true
    &maxAllowableOffset=
    &geometryPrecision=
    &outSR=&returnIdsOnly=false
    &returnCountOnly=false
    &orderByFields=
    &groupByFieldsForStatistics=
    &outStatistics=
    &returnZ=false&returnM=false
    &gdbVersion=
    &returnDistinctValues=false
    &f=pjson
'''


def getToken(username, password, exp=10):
    """Generates a token."""
    ##See https://github.com/mjanikas/devsummit-14-python/blob/master/publish_service.py ##
    referer = "http://www.arcgis.com/"
    query_dict = {'username': username,
    'password': password,
    'client': 'requestip'}
    #'referer': referer}
    query_string = URLLIB.urlencode(query_dict)
    url = "https://www.arcgis.com/sharing/rest/generateToken"
    token = JSON.loads(URLLIB.urlopen(url + "?f=json", query_string).read())
    if "token" not in token:
        print(token['error'])
        SYS.exit()
    else:
        httpPrefix = "http://www.arcgis.com/sharing/rest"
        if token['ssl'] == True:
            httpPrefix = "https://www.arcgis.com/sharing/rest"
        return token['token'], httpPrefix, token['ssl']
    
def getFlowlines(HUC6,outFC,token,ssl):
    msg("Accessing Landscape server...")
    if ssl:
        baseURL = "https://landscape1.arcgis.com/arcgis/rest/services/USA_NHDPlusV2/MapServer/3/query?"
    else:
        baseURL = "http://landscape1.arcgis.com/arcgis/rest/services/USA_NHDPlusV2/MapServer/3/query?"
    query_dict = {'where':"reachcode LIKE '{}%'".format(HUC6),
                 'outFields':'*',
                 'returnGeometry':'true',
                 'f':'json',
                 'token':token}
    query_string = URLLIB.urlencode(query_dict)
    fsURL = baseURL + query_string
    fs = arcpy.FeatureSet()
    msg("Retrieving records")
    fs.load(fsURL)
    msg("Saving records to {}".format(outFC))
    arcpy.CopyFeatures_management(fs,outFC)
    recordCount = arcpy.GetCount_management(Flowlines)
    msg('{} records returned'.format(recordCount))
    return 
