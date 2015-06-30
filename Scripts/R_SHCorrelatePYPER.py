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

# import the Pyper module
import pyper
rPath = r"C:/Program Files/R/R-3.1.1/bin/i386/R"
r = pyper.R(RCMD=rPath)

'''DEBUG INPUTS
C:\WorkSpace\EEP_Spring2015\EEP_Tool\Scratch\RData\E_complanata2.csv
'''

# Input variables
speciesCSV = 'C:/WorkSpace/EEP_Spring2015/EEP_Tool/Scratch/RData/E_complanata2.csv'#arcpy.GetParameterAsText(0)

# Output variables
correlationCSV = os.path.basename(speciesCSV)[:-4] + "_shc.csv"
correlationCSV1 = os.path.basename(speciesCSV)[:-4] + "_shcX.csv"

## ---Functions---
def msg(txt,type="message"):
    if type == "message":
        arcpy.AddMessage(txt)
    elif type == "warning":
        arcpy.AddWarning(txt)
    elif type == "error":
        arcpy.AddError(txt)
    elif type == 'r':
        arcpy.AddMessage("[R:]"+txt)
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



    
##------------------
# sort variables with signif correlations in descending order of absolute correlation
msg("Sorting significant variables in descending order of abolsute correlation")
msg(r('shco <- shc[order(abs(shc$coef),decreasing=TRUE),]'),'r')
# varList = a list of the variables in sorted order (by absolute correlation)
msg(r('varList <- as.numeric(rownames(shco))'),'r')
# sppX = a list of env variable values
msg(r('sppX <- sppAll[,c(-1)]'),'r')
# habData = a list of habitat data for just the significant variables
msg(r('habData <- sppX[,c(varList)]'),'r')
# Create the trapCollin function: traps collinear variables
r('''trapCollin <- function(data) {
  # data, a frame of numeric variables
  nv <- dim(data)[[2]]
  nc <- nv*(nv-1)/2
  v1 <- rep(NA,nc)
  v2 <- rep(NA,nc)
  r <- rep(NA,nc)
  k <- 0
  for (i in 2:nv) {
    for (j in 1:(i-1)) {
        k <- k+1
        v1[k] <- names(data)[i]
        v2[k] <- names(data)[j]
        r[k] <- cor.test(unlist(data[i]),unlist(data[j]))$statistic
    }
  }
  out <- data.frame(cbind(v1,v2,r))
  out <- out[!is.na(v1),]
  out
}''')
# habData2 = habData less the 
#Use the function to screen 
msg(r('habScreen <- trapCollin(habData)'),'r')
