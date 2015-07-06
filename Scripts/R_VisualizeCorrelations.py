#R_VisualizeCorrelations.py
#
# Description: Creates an HTML page with javascript visualization of the
#  Environment variable correlations.
#
# See "http://visjs.org/docs/network/" for info on the methods for displaying this
#
# July 2015
# John.Fay@duke.edu

import sys, os

#Input variables
speciesName = "E_complanata2"
correlationsCSV = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\Correlations.csv'

#Ouptut
visHTML = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\Correlations.html'

#Create lists from the correlation csv file
nodeList = [] 
nodeDict = {}
id = 1
f = open(correlationsCSV,'rt')
headers = f.readline()
dataString = f.readline()[:-1]
while dataString:
    data = dataString.split(",")
    namePairs = (data[0].strip(), data[1].strip())
    for name in namePairs:
        if not name in nodeList:
            nodeList.append(name)
            nodeDict[name] = id
            id += 1
    dataString = f.readline()[:-1]
f.close()

#Make string from nodeList
nodeString = "      nodes = [\n"
#for node,id in nodeDict.items():
for key, value in sorted(nodeDict.iteritems(), key=lambda (k,v): (v,k)):
    nodeString += "        {}id: {}, value : {}, label: '{}'{},\n".format("{",value,value,key,"}")
nodeString += "      ];\n\n"    

#Make edge string from file
edgeString = "      edges = [\n"
f = open(correlationsCSV,'rt')
headers = f.readline()
dataString = f.readline()[:-1]
while dataString:
    data = dataString.split(",")
    #Get the id of the From node
    fromNode = data[0].strip()
    fromID = nodeDict[fromNode]
    #Get the id of the To node
    toNode = data[1].strip()
    toID = nodeDict[toNode]
    #Get the value (correlation value)
    corVal = abs(float(data[2]))
    #Write the value to the string
    print fromNode,fromID,toNode,toID
    edgeString += "        {}from: {}, to: {}, value: {}, title: '{}'{},\n".format("{",fromID,toID,corVal,corVal,"}")
    dataString = f.readline()
f.close()
edgeString += "      ];\n\n"

#Create the output HTML
f = open(visHTML,'wt')
f.write('''<!doctype html>
<html>
<head>
  <title>E_complanata2</title>

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
f.write(nodeString)
f.write(edgeString)
f.write('''      // Instantiate our network object.
      var container = document.getElementById('mynetwork');
      var data = {
        nodes: nodes,
        edges: edges
      };
      var options = {
        nodes: {
          shape: 'dot',
        },
        physics: {
          solver: 'forceAtlas2Based',
                stabilization: true
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
f.close()

        