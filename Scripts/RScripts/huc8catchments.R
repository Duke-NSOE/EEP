# cull habitat data for all NHD catchments in a set of HUC8s ...
huc8catchments <- function(hucs,data) {
  # hucs, a list of HUC8s where a species occurs (from UNIQUE on spp.obs)
  # data, the catchment-scale habitat data (includes HUC8 label)
  culldata <- NULL
  for (i in hucs) {
    x <- data[HUC8==i,]
    culldata <- rbind(culldata,x)
  }
  culldata
}
