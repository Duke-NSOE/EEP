#CSV2ASCII.py
#
# Converts a MaxEnt CSV file into a series of ASCII pseudo rasters that are
# one column wide and several rows long. This enables them to be used as
# projection layers in a MaxEnt run.
#
# Feb 2015
# John.Fay@duke.edu

import sys, os

#Get and open the CSV file; put data into the lines list
inputFN = "Salamander.csv"
file = open(inputFN,'r')
lines = file.readlines()
file.close()

#Create the ASCII header
rowCount = len(lines) - 1
headerLines = 'ncols\t1\nnrows\t{0}\nxllcorner\t0\nxyllcorner\t0\ncellsize\t1\nNODATA_value\t-9999\n'.format(rowCount)

#Make a list of env vars from the header line
lineItems = lines[0].split(",")
for colIdx in range(1,len(lineItems)):
    print colIdx, lineItems[colIdx]
    #Create the output file
    if colIdx < len(lineItems) - 1: #Need to remove the new line char from the last item
        outFN = lineItems[colIdx] + ".asc"
    else:
        outFN = lineItems[colIdx][:-1] + ".asc"
    file = open(outFN,'w')
    #Write the ASCII header lines
    file.write(headerLines)
    #Read the CSV lines and write out the selected column
    for line in lines[1:]:
        if colIdx < len(lineItems) - 1:
            outValue = line.split(",")[colIdx]
        else:
            outValue = line.split(",")[colIdx][:-1]
        file.write(outValue + "\n")
    #Close the file
    file.close()



