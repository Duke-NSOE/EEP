#Set the workspace
workspace = "C:/WorkSpace/EEP_Spring2015/EEP_Tool/Scratch/Etheostoma_flabellare"
setwd(workspace)

#Open biomod2
library(biomod2)

#Read in the data
#AllData <- read.csv("MaxentSWD.csv")
AllData <- read.csv("AllRecords.csv", row.names = 1)

dim(AllData)

#Set the species name
myRespName <- "Etheostoma_flabellare"

#Set the response variable
myResp <- AllData[c(1)]

#Set the explanatory variables
myExpl <- AllData[,4:108]

#Set the biomod data object
myBiomodData <- BIOMOD_FormatingData(resp.var = myResp, expl.var = myExpl)