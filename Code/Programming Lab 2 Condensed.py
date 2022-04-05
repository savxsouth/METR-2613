#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 15:08:42 2022

@author: savannahsouthward
"""

############################################################### 
# File: data_processing.py 
# Version: 2.1.0 
# Author: Savannah Southward (savannahjsouthward@ou.edu)
# Description:  
#   This program reads in raw station data and creates formatted daily files. 
# 
# Version History: 
#   1.0.0 - 3/24/2022 - Initial release 
#
#   1.5.0 - 4/04/2022 - Corrected for neglecting to add a blank data frame which
#                       unknowingly goofed my output files oops...
#
#   2.0.0 - 4/04/2022 - Daily CSVs (filled with -9999s) and curated daily 
#                       statistics for Temperature, Wind Speed, and Total Rainfall
#
#   2.5.0 - 4/04/2022 - Condensed version for Daily CSVs and Summary Reports in
#                       the same while loop
#
# Inputs: 
#  * CSV formatted raw data file from CR300 series datalogger. 
#  * YAML settings file (data_file, data_filename, output_file_path, start_date, end_date)
# 
# Outputs: 
#  * CSV formatted daily files.
#  * Maximum, Minimum, and Average Summary Reports. 
#  
# To Do: 
#  * Finalize and push changes to GitHub
#  * Ask if this is even what I am supposed to be doing
#  
# Bugs: 
#  * None - That I know of...
# 
# Notes: 
#   * All Python libraries are the latest versions as of release date. 
# 
# Copyright (c) 2022 
# Board of Regents, Univ. of Oklahoma  
# All Rights Reserved. 
# Proprietary. Confidential. 
############################################################### 

# Pseudocode:
    
# Import libraries
import os 
import pandas as pd
import numpy as np
import yaml
from pathlib import Path  
from datetime import datetime, timedelta

## Choose the location of the data file
settings_file = Path('/Users/savannahsouthward/opt/anaconda3/envs/METR-2613/Code/settings.yaml') 
with open(settings_file, "r") as f:
    settings = yaml.safe_load(f)
print(settings)

start_date = datetime.strptime(settings['start_date'], "%Y-%m-%d %H:%M")
end_date = datetime.strptime(settings['end_date'], "%Y-%m-%d %H:%M")
current_date = start_date

empty = pd.DataFrame(index=pd.date_range(start_date, end_date, freq='5min'),
                        columns=['RECORD','TAIR','RELH','SRAD','WSPD','WMAX',
                                 'WDIR','RAIN','BATV']).rename_axis('TIMESTAMP')

## Read in raw data file
rawdata = pd.read_csv(settings["data_file"], skiprows = (0, 2, 3), index_col='TIMESTAMP')
rawdata.index = pd.to_datetime(rawdata.index)

## Merge raw data into blank dataframe
data = rawdata.combine_first(empty)
data.reset_index(inplace = True)

# Parse data for the particular day 
data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'])
data = data.drop('RECORD', axis=1)

# Loop through each day (without hard coding!)

# Create the formatted Summary Report File within desired directory
os.chdir(settings["output_file_path"])

sumdate_start =  pd.to_datetime(settings['start_date']).strftime('%Y%m%d')
sumdate_end =  pd.to_datetime(settings['end_date']).strftime('%Y%m%d')

summary = "NWC0_REPORT_" + sumdate_start + "_" + sumdate_end   
file = open(summary+'.txt', 'w')
file.write("Statistics Report \n" "Input file: " + settings["data_filename"] 
               + "\n" "Output Data: ")

# Create the Daily CSVs within desired directory
   
## While Loop to cycle through the data for each day
while current_date <= end_date:
    
## Replace Missing data with -999
    data.fillna('-9999', inplace=True)

## Set up daily dataframe from 00z to 23:55z
    day = data[(data["TIMESTAMP"] >= datetime(current_date.year, current_date.month, current_date.day, 0, 0)) 
                   & (data["TIMESTAMP"] <= datetime(current_date.year, current_date.month, current_date.day, 23, 55))]
  
## File path to directory the csv files need to be saved to
    filepath = settings["output_csv_path"]
    
## File name that fills in the proper datetimes for the data
    filename = "NWC_{}{:02d}{:02d}.dat".format(current_date.year, current_date.month, current_date.day)
    
## CSV Outfile
    outfile = os.path.join(filepath,filename)
    day.to_csv(outfile)
 
###############################################################

# Summary Reports

## Replace -9999s from Daily CSV section with NaNs to mitigate calculation error 
    day = day.replace("-9999", np.NaN)

## Number of lines missing from the data file
   ### Observations are taken at five minute intervals every hour for 24 hours.
    max_obs = ((60/5)*24)
    missing = max_obs - len(day)

## Maximum, minimum, and average temperature
    max_temp = "{:8.2f}".format(day["TAIR"].max())
    min_temp = "{:8.2f}".format(day["TAIR"].min())
    avg_temp = "{:8.2f}".format(day["TAIR"].mean())
    
## Maximum, minimum, and average wind speed
    max_wind = "{:8.2f}".format(day["WSPD"].max())
    min_wind = "{:8.2f}".format(day["WSPD"].min())
    avg_wind = "{:8.2f}".format(day["WSPD"].mean())
    
## Total Rainfall
    total_rf = "{:8.2f}".format(day["RAIN"].max())

# Write the Summary Report File 
    file.write("\n \t File: " + filename + "\n" "\t \t Missing Observations: " + str(missing) + "\n" +
               "\t \t Air Temperature (C):    Max: {:7}    Min: {:7}    Avg: {:7} \n".format(max_temp, min_temp, avg_temp) +
               "\t \t Wind Speed (m/s)   :    Max: {:7}    Min: {:7}    Avg: {:7} \n".format(max_wind, min_wind, avg_wind) +
               "\t \t Precipitation (mm) :   {:7}".format(total_rf))
    
    current_date += timedelta(days = 1)
    
file.close()