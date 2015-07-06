# R_SHCorrelatePYPER.py
#
# Description:
#  Correlate spp presence/absence with habitat variables. The specices CSV should have no NA values.
#
# Spring 2015
# John.Fay@duke.edu

##To load PypeR, uncomment the following (setup tools must be installed)
#from setuptools.command import easy_install
#easy_install.main(["-U","scipy"])

import sys, os, csv, arcpy, numpy

'''DEBUG INPUTS
C:/Program Files/R/R-3.1.1/bin/i386/R C:/WorkSpace/EEP_Spring2015/EEP_Tool/Scratch/RData/E_complanata2.csv C:/WorkSpace/EEP_Spring2015/EEP_Tool/Scratch/RData/E_complanata2_sch.csv C:/WorkSpace/EEP_Spring2015/EEP_Tool/Scratch/RData/E_complanata2_schX.csv
'''

# Input variables
rPath = arcpy.GetParameterAsText(0)
speciesCSV = arcpy.GetParameterAsText(1)

# Output variables
correlationCSV = arcpy.GetParameterAsText(2)
correlationCSV1 = arcpy.GetParameterAsText(3)

# import the Pyper module
import pyper
r = pyper.R(RCMD=rPath)

## ---Functions---
def msg(txt,type="message"):
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)
    elif type == 'r':
        arcpy.AddWarning("[R:]"+txt[5:-4])
        print "[R:]",
    print txt
        
## ---Processes---
#Set the R workspace
msg("Setting the R workspace")
msg(r('setwd("{}")'.format(os.path.dirname(speciesCSV))),'r')

#Read in the CSV file
msg("Reading in the species data")
msg(r('sppAll <- read.csv("{}")'.format(os.path.basename(speciesCSV))),'r')

#Create the SHcor function
msg("Constructing the SHcor function")
r('''SHcor <- function (spp, env, trim = TRUE, alpha = 0.05) 
{
  n <- dim(env)[[2]]
  variable <- colnames(env)
  coef <- rep(NA,n)
  P <- rep(NA,n)
  for (i in 1:n) {
    ct <- cor.test(spp,env[,i])
    coef[i] <- ct$estimate
    P[i] <- ct$p.value
  }
  sec <- data.frame(variable,coef,P)
  sec
}
''')

#Run the SHcor function on the data
msg("Calculating correlations among values")
msg(r('sppHabCor <- SHcor(sppAll$Species,as.matrix(sppAll[,c(-1)]),alpha=0.05)'),'r')

#Write output to CSV file
msg("Writing full correlation values to {}".format(correlationCSV))
msg(r('write.csv(sppHabCor,"{}")'.format(correlationCSV)),'r')

#Eliminate values with p-values > 0.05
msg("Finding significant correlations")
# make a local copy
msg(r('shc <- sppHabCor'),'r')
# set all nonsignificant correlations to NA:
msg(r('shc$coef[shc$P > 0.05] <- NA'),'r')
# keep just the stuff we need:
msg(r('shc <- shc[!is.na(shc$coef),1:2]'),'r')
# write to file
msg("Writing significant correlations to {}".format(correlationCSV1))
msg(r('write.csv(shc,"{}")'.format(correlationCSV1)),'r')
msg("Finished")