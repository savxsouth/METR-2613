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

# Read in data

## Choose the location of the data file
os.chdir("/Users/savannahsouthward/opt/anaconda3/envs/METR-2613/Data/")
rawdata = pd.read_csv("NWC0_05A_L1.dat", skiprows = (0, 2, 3))
print(rawdata)

## Fill in missing data with NaNs
rawdata = rawdata.fillna(-9999)

# Loop through each of the three days 

## Parse data for the particular day 
rawdata["TIMESTAMP"] = pd.to_datetime(rawdata['TIMESTAMP'])
start_date = datetime(2021, 2, 1, 0, 0)
end_date = datetime(2021, 2, 3, 23, 55)
current_date = start_date

## While Loop to cycle through the data for each day
while current_date <= end_date:
    print(current_date)
    day = rawdata[(rawdata["TIMESTAMP"] >= datetime(current_date.year, current_date.month, current_date.day, 0, 0)) 
                   & (rawdata["TIMESTAMP"] <= datetime(current_date.year, current_date.month, current_date.day, 23, 55))]
    
## File path to directory the csv files need to be saved to
    filepath = Path('/Users/savannahsouthward/opt/anaconda3/envs/METR-2613/Data/csv/') 
    
## File name that fills in the proper datetimes for the data
    filename = "NWC_{}{:02d}{:02d}.dat".format(current_date.year, current_date.month, current_date.day)
    print(filename)
    
## CSV Outfile
    day.to_csv(filepath/filename)

    current_date += timedelta(days = 1)