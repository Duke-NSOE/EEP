# STATS_VisualizeCorrelations.py
#
# Description: Creates an HTML page with javascript visualization of the
#  Environment variable correlations. Variables are displayed as nodes and are
#  colored using rankings described in the ResponseVars.xls file, which should be
#  found in the Data folder. 
#
# See "http://visjs.org/docs/network/" for info on the methods for displaying this
#
# July 2015
# John.Fay@duke.edu

import sys, os, arcpy

#Input variables
speciesName = arcpy.GetParameterAsText(0)           # Name of species analyzed
sppCorrelationsCSV = arcpy.GetParameterAsText(1)    # List of variable correlations with presence/absence
envCorrelationsCSV = arcpy.GetParameterAsText(2)    # List of variabel correlations with each other
envRankingsXLS = arcpy.GetParameterAsText(3)        # Table listing the rankings of each variable for selection [static]

#Ouptut
visHTML = arcpy.GetParameterAsText(4)               # Output HTML file that will be displayed in a browser

## ---Functions---
def msg(txt,type="message"):
    print txt
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)
        
#------PROCESSES-------
## Create a ranking/color dictionary. This converts rankings to sequentially darker colors
msg("...creating listing of ranking colors")
colorDict = {}
colorDict["0"] = "{background:'#FCE8EC',border:'gray'}" # Unable to alter with management
colorDict["1"] = "{background:'#FFFFCC',border:'gray'}" # No expected impact from any action
colorDict["2"] = "{background:'#FFCC99',border:'gray'}" # Indirect impact from 1 action
colorDict["3"] = "{background:'#FF9933',border:'gray'}" # Indirect impact from >1 actions
colorDict["4"] = "{background:'#FF5050',border:'gray'}" # Secondary impact from 1 action
colorDict["5"] = "{background:'#FF33CC',border:'gray'}" # Secondary impact from 2 actions
colorDict["6"] = "{background:'#9900CC',border:'gray'}" # Secondary impact from >2 actions
colorDict["7"] = "{background:'#660033',border:'blue'}"    # Direct impact from any action

##Create a dictionary from the fields listed in the species correlations CSV...
## key-value pairs in this dictionary include the variable name and the correlation value
## which is used for the size of the node (larger = more correlated with presence/absence
msg("...creating a list of significant response variables (nodes)")
nodeDict = {}                       #Create a dictionary of field names/id values
id = 1                              #Initialize the ID variable
f = open(sppCorrelationsCSV,'rt')   #Open the file
headers = f.readline()              #Extract/skip the headers line in the CSV
dataString = f.readline()[:-1]      #Convert the text to string (omitting the newline char at the end
while dataString:                   #Loop through each line in the CSV
    data = dataString.split(",")        #Convert text to a list of items
    name = data[0].strip()              #Set the name to be the variable name (1st column)
    coef = data[2].strip()              #Set the coef to be the variable name (3rd column)
    if not name in nodeDict.keys():     #If name isn't in alread included: 
        nodeDict[name] = (id,coef)          #Add the entry to the dictioary (key=name; val=(id, coef)
        id += 1                             #Increase the id counter
    dataString = f.readline()[:-1]      #Read in the next line in the CSV
f.close()                           #Close the file

##Create another dictionary of fields, this one with their ranking
msg("...Reading in variable rankings from rankings file")
rankDict = {}
cur = arcpy.da.SearchCursor(envRankingsXLS,("variable","Ranking"))
for rec in cur:
    varName = rec[0]              # The variable name is the second column
    varRank = str(int(rec[1]))    # The variable rank is the last column 
    rankDict[varName] = varRank   # Add the key:value to the dictionary
del cur
            
##Create string from nodeList in the visjs format
msg("Writing HTML code for variable nodes")
#Start the string
nodeString = "      nodes = [\n"
#Loop through items in the dictionary - but sort them by value (not by variable name)
for key, value in sorted(nodeDict.iteritems(), key=lambda (k,v): (v,k)):
    #Get the coefficient from the species correlation dictionary
    id = value[0]
    coef = value[1]
    #coef = nodeDict[key][1]#sppCorDict[key]
    rank = rankDict[key]
    color = colorDict[rank]
    #Add a new line to the string containing its id, value, and label
    nodeString += "        {0}id:{1},value:{2},label:'{3}',font:'20px Arial black',color:{4}{5},\n".format("{",id,coef,key,color,"}")
#Finish the string
nodeString += "      ];\n\n"    

##Make edge string from file
#Start the string
edgeString = "      edges = [\n"
f = open(envCorrelationsCSV,'rt')      #Open the CSV file (again)
headers = f.readline()              #Read/skip the header file
dataString = f.readline()[:-1]      #Convert the text to string (omitting the newline char at the end
while dataString:                   #Loop through each line in the CSV
    data = dataString.split(",")        #Convert text to a list of items
    fromNode = data[0].strip()          #Get the id of the From node
    fromID = nodeDict[fromNode][0]     
    toNode = data[1].strip()            #Get the id of the To node
    toID = nodeDict[toNode][0] 
    corVal = abs(float(data[2]))        #Get the value (correlation value)
    #Write the value to the string
    edgeString += "        {}from: {}, to: {}, value: {}, title: '{}'{},\n".format("{",fromID,toID,corVal,corVal,"}")
    dataString = f.readline()           #Read in the next line in the CSV
f.close()                           #Close the file
edgeString += "      ];\n\n"        #Finish the string

##Create the output HTML
#Open the file for writing
f = open(visHTML,'wt')

#Insert the first of the boilerplate text (appended with the species name as Title)
f.write('''<!doctype html>
<html>
<head>
  <title>%s</title>''' %speciesName)

#Continue writing boilerplate
f.write('''
  <style type="text/css">
    html, body {
      font: 14pt arial;
    }
    #nav{
        line-height:30px;
        background-color:#eeeeee;
        width:5%;
        float:left;
        padding:5px;	
    }
    #mynetwork {
            width:90%;
            height: 700px;
            float:left;
            padding:10px;	
      border: 1px solid lightgray;
    }
    .input-color {
        position: relative;
    }
    .input-color input {
        padding-left: 40px;
        width: 20px
    }
    .input-color .color-box {
        width: 20px;
        height: 10px;
        display: inline-block;
        background-color: #ccc;
        position: absolute;
        left: 5px;
        top: 12px;
    }
  </style>

  <script type="text/javascript" src="http://visjs.org/dist/vis.js"></script>
  <link href="http://visjs.org/dist/vis.css" rel="stylesheet" type="text/css" />

  <script type="text/javascript">
    var nodes = null;
    var edges = null;
    var network = null;

    function draw() {
      // create people.
      // value corresponds with the age of the person
''')

# Insert the nodeString created above
f.write(nodeString)

# Insert the edgeString created above
f.write(edgeString)

# Complete the boilerplate
f.write('''            // Instantiate our network object.
      var container = document.getElementById('mynetwork');
      var data = {
        nodes: nodes,
        edges: edges
      };
      var options = {
        nodes: {
          shape: 'dot',
        },
                interaction: {
                    navigationButtons: false,
                    selectable: true
                },
                manipulation: {
                    enabled: true,
                    addNode: false,
                    addEdge: false
                }
        };
      network = new vis.Network(container, data, options);

    }
  </script>
</head>
<body onload="draw()">
''')
f.write("<h3>{}</h3>".format(speciesName))
f.write('''<p>
Scale nodes and edges depending on their value. Hover over the edges to get a popup with more information.
</p>
<div id="nav">
Ranks<br>
''')
        
for i in range(8):
    idx = str(i); colorTxt = colorDict[idx]
    color = colorTxt[13:-16]
    writeString =  '    <div class="input-color">\n' 
    writeString += '        <input type="text" value="{}" />\n'.format(idx) 
    writeString += '        <div class="color-box" style="background-color: {};"></div>\n'.format(color)
    writeString += '    </div>'
    f.write(writeString)

f.write('''
</div>
<div id="mynetwork"></div>
</body>
</html>''')

# Close the file
f.close()

# Open the file in a web browser
import webbrowser
new = 2
webbrowser.open(visHTML,new=new)
        