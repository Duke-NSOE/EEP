# cull habitat data for all NHD catchments in a set of HUC8s ...
huc8catchments <- function(hucs,data,huclabel) {
  # hucs, a list of HUC8s where a species occurs (from UNIQUE on spp.obs)
  # data, the catchment-scale habitat data
  # huclabel, the HUC8 for each NHD catchment
  culldata <- NULL
  for (i in hucs) {
    x <- data[data$HUC8==i,]
    culldata <- rbind(culldata,x)
  }
  culldata
}