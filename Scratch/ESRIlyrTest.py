
import arcpy



outName = "foo.shp"

baseURL = "http://ns-a224-jpfay.win.duke.edu:6080/arcgis/rest/services/NHDplusV2/NHD2Features/FeatureServer/{}/query".format(LayerID)
query = "?where={}&outFields=*&returnGeometry=true&f=json&token=".format(where, fields, token)
fsURL = baseURL + query
fs = arcpy.FeatureSet()
fs.load(fsURL)
arcpy.CopyFeatures_management(fs,OutName)