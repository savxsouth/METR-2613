#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 22:36:36 2022

@author: savannahsouthward
"""

############################################################### 
# File: data_processing.py 
# Version: 3.5.0 
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
#   3.0.0 - 4/11/2022 - Added QA support for Daily CSVs and Summary Reports
#
#   3.5.0 - 4/11/2022 - Condensed version earlier update
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
#  * FIX THIS
#  * Ask if this is even what I am supposed to be doing
#  
# Bugs: 
#  * This whole thing is a mess
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

# Choose the location of the data file
## Choose the location of the data file
settings_file = Path('/Users/savannahsouthward/opt/anaconda3/envs/METR-2613/Code/settings.yaml') 
with open(settings_file, "r") as f:
    settings = yaml.safe_load(f)
print(settings)

start_date = datetime.strptime(settings['start_date'], "%Y-%m-%d %H:%M")
end_date = datetime.strptime(settings['end_date'], "%Y-%m-%d %H:%M")
current_date = start_date

## Raw data file without missing data filled 
raw_datafile = pd.read_csv(settings["data_file"], skiprows = [0, 2, 3])
raw_datafile["TIMESTAMP"] = pd.to_datetime(raw_datafile["TIMESTAMP"])

# Summary Report with QA-ed Data
# Create the formatted Summary Report File within desired directory
os.chdir(settings["output_file_path"])

settings['start_date'] = datetime.strptime(settings['start_date'], "%Y-%m-%d %H:%M")
settings['end_date'] = datetime.strptime(settings['end_date'], "%Y-%m-%d %H:%M")

empty = pd.DataFrame(index=pd.date_range(settings['start_date'], settings['end_date'], freq='5min'),
                        columns=['RECORD','TAIR','RELH','SRAD','WSPD','WMAX','WDIR','RAIN','BATV']).rename_axis('TIMESTAMP')

# Read in raw data file
rawdata = pd.read_csv(settings['data_file'], skiprows=[0,2,3], index_col='TIMESTAMP')
rawdata.index = pd.to_datetime(rawdata.index)

# Merge raw data into blank dataframe
data = rawdata.combine_first(empty)
data.reset_index(inplace = True)

## Parse data for the particular day 
data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'])
data = data.drop('RECORD', axis=1)

start_date = settings['start_date']
end_date = settings['end_date']

data["TAIR"] = data["TAIR"].apply(lambda row: -998 if ((row < settings["variable"]["TAIR"]["QA"]["low_limit"]) or (row > settings["variable"]["TAIR"]["QA"]["high_limit"])) else row)
data["RELH"] = data["RELH"].apply(lambda row: -998 if ((row < settings["variable"]["RELH"]["QA"]["low_limit"]) or (row > settings["variable"]["RELH"]["QA"]["high_limit"])) else row)
data["SRAD"] = data["SRAD"].apply(lambda row: -998 if ((row < settings["variable"]["SRAD"]["QA"]["low_limit"]) or (row > settings["variable"]["SRAD"]["QA"]["high_limit"])) else row)
data["WSPD"] = data["WSPD"].apply(lambda row: -998 if ((row < settings["variable"]["WSPD"]["QA"]["low_limit"]) or (row > settings["variable"]["WSPD"]["QA"]["high_limit"])) else row)
data["WMAX"] = data["WMAX"].apply(lambda row: -998 if ((row < settings["variable"]["WMAX"]["QA"]["low_limit"]) or (row > settings["variable"]["WMAX"]["QA"]["high_limit"])) else row)
                                                                                                                                                           
qa_stats = data.copy()                                                                                                                                                      
qa_stats = qa_stats.replace(-998, np.nan)

data.fillna('-9999', inplace=True)

sumdate_start =  pd.to_datetime(settings['start_date']).strftime('%Y%m%d')
sumdate_end =  pd.to_datetime(settings['end_date']).strftime('%Y%m%d')

qa_summary = "NWC0_REPORT_" + sumdate_start + "_" + sumdate_end   
file = open(qa_summary+'.txt', 'w')
file.write("Statistics Report (QA) \n" "Input file: " + settings["data_filename"] 
               + "\n" "Output Data: ")
   
# While Loop to cycle through the data for each day
while current_date <= end_date:
    print(current_date)
    day = data[(data["TIMESTAMP"] >= datetime(current_date.year, current_date.month, current_date.day, 0, 0)) 
                   & (data["TIMESTAMP"] <= datetime(current_date.year, current_date.month, current_date.day, 23, 55))]

# Create the Daily CSVs within desired directory
    
## File path to directory the csv files need to be saved to
    filepath = Path('/Users/savannahsouthward/opt/anaconda3/envs/METR-2613/Data/csv/') 
    
## File name that fills in the proper datetimes for the data
    filename = "NWC_{}{:02d}{:02d}.dat".format(current_date.year, current_date.month, current_date.day)
    print(filename)
    
## CSV Outfile
    day.to_csv(filepath/filename)
    
############################################################### 

# Summary Reports

## Set up daily dataframe from 00z to 23:55z using the raw data file

    day = data.copy()
    day.reset_index(inplace = True)
    day['TIMESTAMP'] = pd.to_datetime(day['TIMESTAMP'])
    
    daystats = qa_stats.copy()
    daystats.reset_index(inplace = True)
    daystats['TIMESTAMP'] = pd.to_datetime(daystats['TIMESTAMP'])
    
## Set up daily dataframe from 00z to 23:55z
    start_time = datetime(current_date.year, current_date.month, current_date.day, 0, 0)
    end_time = datetime(current_date.year, current_date.month, current_date.day, 23, 55)
    
    daily = day[(day["TIMESTAMP"] >= start_time) & ((day["TIMESTAMP"] <= end_time))]
    dailystats = daystats[(daystats["TIMESTAMP"] >= start_time) & ((daystats["TIMESTAMP"] <= end_time))]

## Number of lines missing from the data file
   ### Observations are taken at five minute intervals every hour for 24 hours.
    obs = raw_datafile[(raw_datafile["TIMESTAMP"] >= datetime(current_date.year, current_date.month, current_date.day, 0, 0))
               & (raw_datafile["TIMESTAMP"] <= datetime(current_date.year, current_date.month, current_date.day, 23, 55))]
    max_obs = ((60/5)*24)
    missing = max_obs - len(obs)

## Maximum, minimum, and average temperature
    max_temp = "{:8.2f}".format(dailystats["TAIR"].max())
    min_temp = "{:8.2f}".format(dailystats["TAIR"].min())
    avg_temp = "{:8.2f}".format(dailystats["TAIR"].mean())
    
## Maximum, minimum, and average wind speed
    max_wind = "{:8.2f}".format(dailystats["WSPD"].max())
    min_wind = "{:8.2f}".format(dailystats["WSPD"].min())
    avg_wind = "{:8.2f}".format(dailystats["WSPD"].mean())
    
## Total Rainfall
    total_rf = "{:8.2f}".format(dailystats["RAIN"].max())

# Write the Summary Report File 
    file.write("\n \t File: " + filename + "\n" "\t \t Missing Observations: " + str(missing) + "\n" +
               "\t \t Air Temperature (C):    Max: {:7}    Min: {:7}    Avg: {:7} \n".format(max_temp, min_temp, avg_temp) +
               "\t \t Wind Speed (m/s)   :    Max: {:7}    Min: {:7}    Avg: {:7} \n".format(max_wind, min_wind, avg_wind) +
               "\t \t Precipitation (mm) :   {:7}".format(total_rf))
    
    current_date += timedelta(days = 1)
    
file.close()