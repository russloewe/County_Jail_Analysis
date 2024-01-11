# Filename: collect_csvs.r
# Author: @russl_corey <russl_corey@proton.me>
# Date: Mar 10, 2023
# 
# This program is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with 
# this program. If not, see <https://www.gnu.org/licenses/>. 


library(readr)
library(stringr)
library(dplyr)

# set working directory to data folder
setwd('/home/russell/Dropbox/DataAnalysis/Lane_County_Jail/')
csv_folder <- "/home/russell/Documents/scrape_jail/"

# Make a list of all the available csv files
files <- paste0(csv_folder, list.files(csv_folder, pattern='.csv$'))

# init empty var for data
csv_data <- c()

for(file in files){
  # update user
  print(paste('processing: ', file))
  
  # read csv file
  data <- read_csv(file)
  
  # append loaded data to dataframe
  csv_data <- rbind(csv_data, data)
}

# cleanup
rm(data)

# save records
write_csv(csv_data, 'data/inmate_list.csv')

