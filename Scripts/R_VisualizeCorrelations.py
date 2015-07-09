#R_VisualizeCorrelations.py
#
# Description: Creates an HTML page with javascript visualization of the
#  Environment variable correlations.
#
# See "http://visjs.org/docs/network/" for info on the methods for displaying this
#
# July 2015
# John.Fay@duke.edu

import sys, os, arcpy

#Input variables
speciesName = arcpy.GetParameterAsText(0)#"E_complanata2"
sppCorrelationsCSV = arcpy.GetParameterAsText(1)#r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\E_complanata2cor.csv'
envCorrelationsCSV = arcpy.GetParameterAsText(2)#r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\Correlations.csv'

#Ouptut
visHTML = arcpy.GetParameterAsText(3)#r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\Correlations.html'

#------PROCESSES-------
## Create a dictionary of species correlation values from the sppCorrelation CSV file
sppCorDict = {}
f = open(sppCorrelationsCSV,'rt')   #Open the file
headers = f.readline()              #Extract/skip the headers line in the CSV
dataString = f.readline()[:-1]      #Convert the text to string (omitting the newline char at the end
while dataString:                   #Loop through each line in the CSV
    data = dataString.split(",")        #Convert text to a list of items
    varName = data[0].strip()           #Get the variable name (1st item)
    coef = data[1].strip()              #Get the coefficient
    sppCorDict[varName] = coef          #Add items to the dictionary
    dataString = f.readline()[:-1]      #Read in the next line in the CSV    

'''
##Create dictionary from the fields listed in correlations CSV file. Keys in the dictionary
##  are the field names and the values are a unique ID which can be used to link nodes to edges
nodeDict = {}                       #Create a dictionary of field names/id values
id = 1                              #Initialize the ID variable
f = open(envCorrelationsCSV,'rt')   #Open the file
headers = f.readline()              #Extract/skip the headers line in the CSV
dataString = f.readline()[:-1]      #Convert the text to string (omitting the newline char at the end
while dataString:                   #Loop through each line in the CSV
    data = dataString.split(",")                    #Convert text to a list of items
    namePairs = (data[0].strip(), data[1].strip())  #Extract the two field names
    for name in namePairs:                          #See if the names are already in the dictionary
        if not name in nodeDict.keys():             #If not, add them and give them a unique ID
            nodeDict[name] = id
            id += 1
    dataString = f.readline()[:-1]                  #Read in the next line in the CSV
f.close()                           #Close the file
'''
##Create a dictionary from the fields listed in the species correlations CSV...
nodeDict = {}                       #Create a dictionary of field names/id values
id = 1                              #Initialize the ID variable
f = open(sppCorrelationsCSV,'rt')   #Open the file
headers = f.readline()              #Extract/skip the headers line in the CSV
dataString = f.readline()[:-1]      #Convert the text to string (omitting the newline char at the end
while dataString:                   #Loop through each line in the CSV
    data = dataString.split(",")                    #Convert text to a list of items
    name = data[0]
    if not name in nodeDict.keys():             #If not, add them and give them a unique ID
        nodeDict[name] = id
        id += 1
    dataString = f.readline()[:-1]                  #Read in the next line in the CSV
f.close()                           #Close the file

##Create string from nodeList in the visjs format
#Start the string
nodeString = "      nodes = [\n"
#Loop through items in the dictionary - but sort them by value (not by variable name)
for key, value in sorted(nodeDict.iteritems(), key=lambda (k,v): (v,k)):
    #Get the coefficient from the species correlation dictionary
    coef = sppCorDict[key]
    #Add a new line to the string containing its id, value, and label
    nodeString += "        {}id: {}, value : {}, label: '{}'{},\n".format("{",value,coef,key,"}")
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
    fromID = nodeDict[fromNode]     
    toNode = data[1].strip()            #Get the id of the To node
    toID = nodeDict[toNode]
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
    #mynetwork {
      width: 100%;
      height: 800px;
      border: 1px solid lightgray;
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
<p>
  Scale nodes and edges depending on their value. Hover over the edges to get a popup with more information.
</p>
<div id="mynetwork"></div>
</body>
</html>''')

# Close the file
f.close()

# Open the file in a web browser
import webbrowser
new = 2
webbrowser.open(visHTML,new=new)
        