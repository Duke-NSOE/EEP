#See http://finzi.psych.upenn.edu/library/biomod2/doc/Simple_species_modelling.pdf

#Set the workspace
workspace = "D:/Workspace/EEP/Scripts/Biomod2Scripts"
setwd(workspace)

#Read in the data csv file
all.data <- read.csv("AllRecords.csv",head=TRUE,sep=",")

#Create the species vector
all.spp <- as.numeric(all.data$Species)

#Create the habitat variables matrix
all.env <- all.data[,c(4:108)]
