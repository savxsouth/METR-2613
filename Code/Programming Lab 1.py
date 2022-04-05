#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 12:15:05 2022

@author: savannahsouthward
"""

############################################################### 
# File: data_processing.py 
# Version: 1.0.0 
# Author: Savannah Southward (savannahjsouthward@ou.edu)
# Description:  
#   This program reads in raw station data and creates formatted daily files. 
# 
# Version History: 
#   1.0.0 - 3/24/2022 - Initial release 
#
#   1.5.0 - 4/04/2022 - Corrected for neglecting to add a blank data frame which
#                       unknowingly goofed my output files oops...
# Inputs: 
#  * CSV formatted raw data file from CR300 series datalogger. 
# 
# Outputs: 
#  * CSV formatted daily files. 
#  
# To Do: 
#  * Remove the “RECORD” column of data.  
#  
# Bugs: 
#  * None 
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
from pathlib import Path  
from datetime import datetime, timedelta

# Choose the location of the data file
os.chdir("/Users/savannahsouthward/opt/anaconda3/envs/METR-2613/Data/")
data_file = "NWC0_05A_L1.dat"

# Loop through each of the three days 
start_date = datetime(2021, 2, 1, 0, 0)
end_date = datetime(2021, 2, 3, 23, 55)
current_date = start_date

# Set up blank dataframe

empty = pd.DataFrame(index=pd.date_range(start_date, end_date, freq='5min'),
                        columns=['RECORD','TAIR','RELH','SRAD','WSPD','WMAX',
                                 'WDIR','RAIN','BATV']).rename_axis('TIMESTAMP')

# Read in raw data file
rawdata = pd.read_csv(data_file, skiprows=[0,2,3], index_col='TIMESTAMP')
rawdata.index = pd.to_datetime(rawdata.index)

# Merge raw data into blank dataframe
data = rawdata.combine_first(empty)
data.reset_index(inplace = True)

## Parse data for the particular day 
data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'])
data = data.drop('RECORD', axis=1)

## Replace Missing data with -999
data.fillna('-9999', inplace=True)

# While Loop to cycle through the data for each day
while current_date <= end_date:
    print(current_date)
    day = data[(data["TIMESTAMP"] >= datetime(current_date.year, current_date.month, current_date.day, 0, 0)) 
                   & (data["TIMESTAMP"] <= datetime(current_date.year, current_date.month, current_date.day, 23, 55))]
    
## File path to directory the csv files need to be saved to
    filepath = Path('/Users/savannahsouthward/opt/anaconda3/envs/METR-2613/Data/csv/') 
    
## File name that fills in the proper datetimes for the data
    filename = "NWC_{}{:02d}{:02d}.dat".format(current_date.year, current_date.month, current_date.day)
    print(filename)
    
## CSV Outfile
    day.to_csv(filepath/filename)

    current_date += timedelta(days = 1)