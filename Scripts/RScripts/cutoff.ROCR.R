# Return the optimum cut-off value for a predictor 
# from an ROCR object.
#
# There are three methods:
# method="tpr", target=0.95 is appropriate of presence-only models
#   and returns the cut-off level that most closely meets the
#   target rate of TPRs (default=0.95).
# method="max" is for true presence/absence models; it finds the 
#   cut-off value that maximizes the sum of Se and Sp.
# method="x" is for presence/absence models, too, but finds the
#   cut-off where Se=Sp (i.e., intersects the two curves).
# Either of the P/A methods will work for presence-only models,
# if interpreted appropriately.
#
# DL Urban (29 Jan 2008)

cutoff.ROCR <- function(pred, method="max", target=0.95) {
# This uses ROCR's functions:
	require('ROCR')
# The argument "pred" must be a prediction object from ROCR.
#
	METHODS <- c("max","x","tpr")
	method <- pmatch(method, METHODS)
	if (is.na(method)) 
		stop("invalid method")
	if (method == -1) 
		stop("ambiguous method")

# Build the performance object. Use (1-FPR)=TNR so the x.measure
# scales properly relative to TPR.
	perf<-performance(pred,measure="tpr",x.measure="tnr")
 
# (1) method=1: maximum Se+Sp, an appropriate tuning is to 
# find the max sum of TPR and TNR (which finds the max PHI).
	if (method==1) 
# The index of the cut-off value that maximizes the sum of Se and Sp:
		ic<-which.max(perf@x.values[[1]]+perf@y.values[[1]])

# (2) method=2:  find the intersection of Se and Sp:
	if (method==2) 
		ic<-which.min(abs(perf@y.values[[1]] - perf@x.values[[1]]))

# method=3:  target a user-specified TPR (default=0.95):
	if (method==3)
		ic <- which.min(abs(perf@y.values[[1]] - target))

	cut <- perf@alpha.values[[1]][ic]
	cut
}
