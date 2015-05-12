# compute frequencies from a data frame ...
tally.NAs <- function(x) {
  nr <- nrow(x)
  nc <- ncol(x)
  count <- rep(NA,nc)
  freq <- as.vector(rep(NA,nc))
  for (i in 1:nc) {
    a <- x[,i]
    count[i] <- length(a[is.na(a)])
  }
  freq <- count/nr
  out <- cbind(names(x),count,freq)
  out
}