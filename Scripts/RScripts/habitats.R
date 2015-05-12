# ***
# Processing location and habitat data for EEP project ...
# ***
# DL Urban (May 2015)
#
# the data files:
#
#   spp_freqs.csv = frequency of occurrence in NHD+ catchments, by species
#   [spp.freqs on reading it in]
#   huc_30501.csv (or similar) = NHD catchment data for this huc6, which is the santee (includes cawtawba)
#   [huc.data on read]
#   huc30501_attributes.csv (or similar0 = labels, including HUC8
#   [huc.atts on read]

# logic:
#
#    cull catchments for spp X from spp.freqs
#	(1) pull habitat data from huc.data for all catchments with this spp 
#     = presences;
#	(2) cull HUC8s for this spp, which is all HUC8s in which that spp occurred (in spp.freqs);
#	    pull habitat data for all catchments in all HUC8s where this spp occurred = available.
#     (these steps are commented explicitly in the code below)

# ***
# read data files ...
# ***

spp.freqs <- read.csv("spp_freqs.csv")
# 5926 x 420 (= FEATUREID, REACHCODE, HUC6/8/12 + 415 spp)
# test spp ...
# these are the greenfin, fieryblack, and greenhead shiners (in order);
# the greenhead is an indicator spp suggested by bryn.
spp.test <- spp.freqs[,c(1:5,96,101,311)]
# n.b. all we really need here is FEATUREID, HUC8, and the 1 species of interest;
# see line tagged # *** below

# the catchment data ...
# *** n.b. we need to know ALL the missing value codes for this to work!
huc.data <- read.csv("030501_condensed.csv", na.strings=c("NA","-9,998.00","-9,999.00"))
names(huc.data)
dim(huc.data)
# 17034 x 71 (FEATUREID = NHD+ catchment is column 1)

# get the attribute data (need HUC8):
huc.atts <- read.csv("030501_Attributes_WithHUC.csv")
dim(huc.atts)
names(huc.atts)
# 17034 x 10;need 2 & 9, which are featureID and HUC8

# bandaid code:  we need HUC8 in the data, for convenience:
HUC8 <- huc.atts$HUC8
FEATUREID <- huc.data$FEATUREID
huc.data <- cbind(FEATUREID,HUC8,huc.data[,-1])

# get the species 'presence' data...FEATUREID, HUC8, spp ..
# *** all we need is these 3 columns:
spp.obs <- spp.test[spp.test$Notropis_chlorocephalus>0,c(1,4,8)]
# relabel the species, for convenience
names(spp.obs)[3] <- "spp" 
# collapse to presence/absence (the data are in reported cases/occurrences now):
spp.obs$spp <- 1

# (step 1) match-merge on featureID, discarding habitat samples that don't match ...
# by default, this merges on shared columns (here, FEATUREID) and discards mismatches;
# that is, cull habitat data for all the catchments that recorded this species:
spp.data <- merge(spp.obs[,1:2], huc.data)
dim(spp.data) # check sample size
names(spp.data) # just to be sure ...

# and the 'available' HUC8s ...
# HUC8s in which this species oocurred:
spp.huc8s <- unique(spp.obs$HUC8)

# this function culls all the catchments in the HUC8s in which the spp was found:
# (step 2), the "background" data
# *** uses utility function huc8catchments.R
source("huc8catchments.R")
spp.bckgrnd <- huc8catchments(spp.huc8s,huc.data)

# need "spp" label:  1 = presence, 0=background
spp.p <- rep(1,dim(spp.obs)[1])
spp.b <- rep(0,dim(spp.bckgrnd)[1])
spp <- c(spp.p,spp.b)

# pool ...
spp.all <- rbind(spp.data,spp.bckgrnd)
# and attach the "spp" label:
spp.all <- cbind(spp,spp.all)
# check sample sizes:
length(spp.all$spp[spp.all$spp==1])
length(spp.all$spp[spp.all$spp==0])

# ***
# end data assembly; now comes exploratory data analysis and editing ...
# ***

# find NA's (this could be done at any time, e.g., with huc.data)
# *** uses utility function tally_NAs.R
source("tallyNAs.R")
NA.freqs <- tally.NAs(spp.all)
# print, and pull variables that have NAs ...
NA.freqs 
# here, it's V0001E:
# use names(spp.all) to find the column numbers corresponding to these variables
spp.all <- spp.all[,-9]
names(spp.all)
# get correlations between this spp and the habitat variables ...
# uses utility function SEcor.R;
# exclude the labels up front (FEATUREID, ...):
spp.hab.cor <- SHcor(spp.all$spp,as.matrix(spp.all[,c(-1,-2,-3)]),alpha=0.05)
# a list with habitat variable name, correlation, and P value per variable:
spp.hab.cor
# n.b. for the greenhead shiner this creates a NA cuz QLOSS001 has a
# SD of 0 and so divides by 0
# save it (note renaming):
write.csv(spp.hab.cor, "greenhead_shiner_shc.csv")

# this works (!) ...
shc <- spp.hab.cor # a local copy
# set all nonsignificant correlations to NA:
shc$coef[shc$P > 0.05] <- NA
# keep just the stuff we need:
shc<- shc[!is.na(shc$coef),1:2]
write.csv(shc,"greenhead_shiner_shcX.csv")
# variables with signif correlations, sorted in descending order of absolute correlation:
shco <- shc[order(abs(shc$coef),decreasing=TRUE),]
# scan, to see what's going on with this spp;

var.list <- as.numeric(rownames(shco))
spp.x <- spp.all[,c(-1,-2,-3)]
hab.data <- spp.x[,c(var.list)]
names(hab.data)

# check correlations among these:
# utility function screen_cor.R:
hab.screen <- screen.cor(hab.data)
hab.screen
names(hab.data)
# edit by hand? (I don't know how to automate this) ...
# remove the offending variables:
hab.data <- hab.data[,c(-10)]
# recycle thru these last few lines (screen.cor thru the edit)
# until you're satisfied with the remaining variables.

# ***
# end EDA;
# ready to do an actual analysis!
# ***

#	fit GLM for spp X
#	  tune to 95% true positive rate (use cutoff.ROCR)
#	  predict for all catchments in the analysis unit (here, the "available" sample)
#	dump:  prediction [0,1]; prediction as "habitat/not" [1/0]

# fit the model:
spp.glm <- glm(as.factor(spp)~., data=hab.data, family=binomial)
summary(spp.glm)
spp.glm.anova <- anova(spp.glm, test="Chi")
# might want to save this as a CSV?
# model deviance explained (~ R2):
spp.glm.d2 <- 1-(spp.glm$deviance/spp.glm$null.deviance)
spp.glm.d2

# for fun:  a jackknifing estimate of variable importance:
source("jackGLM.R")
spp.jtable <- jackGLM(spp,hab.data)
spp.jtable
write.csv(spp.jtable, "greenhead_shiner_jtable.csv")

# threshold to a binary prediction:
spp.glm.pred <- predict(spp.glm, data=hab.data)
library(ROCR)
source("cutoff.ROCR.R")
# create a "prediction" object (table of predicted & actual values):
spp.pred <- prediction(spp.glm$fitted.values, spp)
cutoff <- cutoff.ROCR(spp.pred, "tpr", target=0.95)
spp.glm.pred[spp.glm.pred<cutoff] <- 0
spp.glm.pred[spp.glm.pred>=cutoff] <- 1
# the confusion matrix:
table(spp.glm.pred,spp)

# redo, to generate prediction for the HUC6 study area (the background samples):
spp.glm.pred2 <- predict(spp.glm, data=spp.all[spp.all$spp==0,])
# copy before thresholding:
spp.glm.pc <- spp.glm.pred2
spp.glm.pred2[spp.glm.pred2<cutoff] <- 0
spp.glm.pred2[spp.glm.pred2>=cutoff] <- 1
write.csv(cbind(spp.glm.pc,spp.glm.pred2),"greenhead_shiner_pred.csv")

# ***
# end GLM
#



# alt 2:  dump spp.all to maxent (code "spp" as "spp" vs "background")
# to run externally, dump spp.all ...
# relabel 'spp' first:
spp.mxdata <- spp.all
spp.mxdata$spp[spp.mxdata$spp==1] <- "greenhead.shiner"
spp.mxdata$spp[spp.mxdata$spp==0] <- "background"
write.csv(spp.mxdata, "greenhead_shiner_mxdata.csv")


# alt 3:  dump "presences" to mahalnobis; 
# MD2 is (ecological) distance from the centroid of presence points...
# presences only:
spp.pres <- hab.data[spp==1,]
# vector of means on the habitat variables:
spp.means <- apply(spp.pres,2,mean)
background.hab <- hab.data[spp==0,]
spp.cov <- cov(background.hab)
# spp.icov <- solve(cov)
# MD2 values for all catchments:
spp.md2 <- mahalanobis(background.hab,spp.means,spp.cov)
summary(spp.md2)
# convert to probabilities, from the Chi-sq distribution:
spp.md2.p <- ???  # figure out how to convert from value to P:  is it qchisq?

# some exploratory stuff to confirm that MD2 is appropriate ...



