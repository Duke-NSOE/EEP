# R_CreateHabitatScript.py
#
# Description: Creates an R script to evaluate a species
#
# Spring 2015
# John.Fay@duke.edu

import sys, os, csv

# Input variables
speciesName = 'E_complanata'
speciesCSV = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\E_complanata2.csv' #Output from R_CreateDataFile.py
scriptsFldr = r'C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scripts\RScripts'

# Script variables
basePath = os.path.dirname(speciesCSV)
## Output files
SHCoutput = os.path.join(basePath,speciesName + "_shc.csv")
SHCXoutput = os.path.join(basePath,speciesName + "_shcX.csv")
## R Scripts
SHcor_R = os.path.join(scriptsFldr,"SHcor.R")
screen_cor_R = os.path.join(scriptsFldr,"screen_cor.R")

# Output variables
outScript = os.path.join(basePath,speciesName + "_habmod.R")

##---- PROCESSES ------
# Create a list of variable inputs
inputList = (speciesName,   #0 Species Name
             speciesCSV,    #1 Input data file
             SHcor_R,       #2 SHcor.R script
             SHCoutput,     #3 Correlation variable output file
             SHCXoutput,    #4 Significant correlated variable output file
             screen_cor_R,  #5
             )

writeString = \
'''####Habitat model for {0}#####
#Read the data file
spp.all <- read.csv("{1}")
#Load the correlation script
source("{2}")
#Run the coorelation
spp.hab.cor <- SHcor(spp.all$Species,as.matrix(spp.all[,c(-1)]),alpha=0.05)
#Save the full correlation results
write.csv(spp.hab.cor,"{3}")
#Create a local copy
shc <- spp.hab.cor
#Keep just the stuff we need
shc$coef[shc$P > 0.05] <- NA
#Save the culled variables
write.csv(shc,"{4}")
# variables with signif correlations, sorted in descending order of absolute correlation:
shco <- shc[order(abs(shc$coef),decreasing=TRUE),]
# scan, to see what's going on with this spp;
var.list <- as.numeric(rownames(shco))
spp.x <- spp.all[,c(-1)]
hab.data <- spp.x[,c(var.list)]
names(hab.data)
# check correlations among these:
# utility function screen_cor.R:
#source("{5}")
#hab.screen <- screen.cor(hab.data)
#hab.screen
'''.format(*inputList)

# Switch the slashes
outString = writeString.replace("\\","/")

# Open the file for writing
outFile = open(outScript,'wb')
outFile.writelines(outString)
outFile.close()