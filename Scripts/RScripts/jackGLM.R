# jackGLM provides jack-knifed estimates of the explanatory 
# power of predictive variables in a generalized linear model. 
# The approach mimics that used in maxent and my earlier attempt
# to mimic this using classification trees (jackTREE).
# The index of explanatory power is approx R2 on sole inclusion
# and on withholding (each variable left out in turn).
# This version uses only logistic regression but could be extended. 


jackGLM <- function(spp, data)
	# the inputs: spp=presence/absence of a species, coded 1/0;
	# data is a frame of predictor variables
{
	# the D2 and P-value for the full model:
	full<-rep(NA,2)
	names(full)<-c("D2","P")
	# build a table for the jack-knifed estimates of explanatory power:
	nv <- ncol(data)
	d2in<-rep(NA,nv) # R2 as deviance explained by the model with only this variable
	pin<-rep(NA,nv)	# P-value for this model
	d2out<-rep(NA,nv)  # R2 for the model with this variable withheld (all other vars in)
	pout<-rep(NA,nv)  # P-value for this model
	jtable<-data.frame(cbind(d2in,pin,d2out,pout))
	vn <- names(data)
	names(jtable)<-c("D2only","Ponly","dD2without","Pwithout")
	rownames(jtable)<-vn

	# run the full model:
	gfull<-glm(as.factor(spp)~.,data=data,family=binomial)
	# D2 and P for the full model:
	d2full <- 1 - (gfull$deviance/gfull$null)
	pfull <- 1 - pchisq(gfull$null - gfull$deviance, (nv+1))
  	full<-c(d2full,pfull)

	# do each variable ...
    	for (i in 1:nv) {
		# this variable only in the model:
		gin<-glm(as.factor(spp)~data[,i],family=binomial)
		# D2:
		d2ii<- 1 - (gin$deviance/gin$null)
		# P-value:
		pii<- 1 - pchisq(gin$null - gin$deviance, 2)
		jtable[i,1]<-d2ii
		jtable[i,2]<-pii
		# everything except this variable:
		gix<-glm(as.factor(spp)~.,data=data[,-i],family=binomial)
		d2ix<- 1 - (gix$deviance/gix$null)
		dd2ix<-d2full-d2ix # we want the difference in D2 from the full model
		aix<-anova(gix,gfull,test="Chi") # does this variable add to the model?
		pix<-aix$"Pr(>Chi)"[[2]] # the P-value on the 2nd model, with the variable added
		jtable[i,3]<-dd2ix
		jtable[i,4]<-pix
	}
	return(list(full,jtable=jtable))
}
