#!/usr/bin/python
# Copyright 2014 Karthikeyan Chellappa

# INPUTS
# navData.csv

# ASSUMPTIONS
# Monthly investment - Rs. 1,000

# DESIRED OUTPUT
# generate output files for each column (goes into an output directory)
# output files should contain the txn details for the specific fund
# create a summary file that provides the xirr for each fund and overall average
# summary file should also show sharpe ratio for annual & half-yr returns

# LOGIC
# Shrink NAV data to start from 01-Jan-2008
# Create an output folder if it doesn't exist
# Loop from column 1 to n (store the date column separately)
# Create a (date, nav) array for the selected fund
# Compute the units invested each month and save to an output file
# For every 6 months, compute the sharpe ratio
# For every 12 months, compute the sharpe ratio
# For the overall period, compute the sharpe ratio
# Compute the XIRR for the whole period
# Store the output details (xirr, sharpe) in a dictionary
# At the end of the loop, generate a summary file

import os
import sys
from datetime import datetime
import common
import financial
import sharpeRanking

start_date = '01-01-2008'
data_dir = 'data/rs'
mnt_inv = 1000

def get_wealth(nav_dict, units_dict):
  wealth = {}
  for fund in units_dict:
    wealth[fund] = float(nav_dict[fund]) * float(units_dict[fund])
  return wealth

def stats(nav_data):
  
  # create data directory if it doesn't exist
  if not os.path.exists(data_dir):
    print 'creating output directory - %s' % data_dir
    os.makedirs(data_dir)
  
  # remove the first 12 entries in nav_data to compare with benchmark
  del nav_data[1:14]

  # retrieve fund names
  fund_names = nav_data[0].split(',')

  # initialize units dictionary
  units_dict_halfyr = common.init_dict(fund_names, 0)
  units_dict_annual = common.init_dict(fund_names, 0)
  units_dict_overall = common.init_dict(fund_names, 0)

  # initialize cashflows array
  cashflows_halfyr = common.init_dict(fund_names, [])
  cashflows_annual = common.init_dict(fund_names, [])
  cashflows_overall = common.init_dict(fund_names, [])
  
  # initialize returns array
  returns_halfyr = common.init_dict(fund_names, 0)
  returns_annual = common.init_dict(fund_names, 0)
  
  # remove header line
  del nav_data[0]

  # compute cashflows and returns
  cnt = len(nav_data)
  for i in range(0, cnt):
    nav_line = nav_data[i].split(',')
    dt = datetime.strptime(nav_line[0], '%d-%m-%Y')
    
    num_cols = len(nav_line)
    for j in range(1, num_cols):
    
      # compute returns every 6 months
      if i % 6 == 0 and i > 0:
        pass
        
      # compute returns every year
      if i % 12 == 0 and i > 0:
        pass
      
      # No investment on the last date
      if i == cnt - 1:
        break
      
      fund = fund_names[j]
      units = mnt_inv / float(nav_line[j])
      units_dict_halfyr[fund] += units
      units_dict_annual[fund] += units
      units_dict_overall[fund] += units
    
      # cash outflow
      cf = (dt, -mnt_inv)
      cashflows_halfyr[fund].append(cf)
      cashflows_annual[fund].append(cf)
      cashflows_overall[fund].append(cf)    
      
    break
      
  # total investment amount
  num_inv = len(nav_data) - 1
  total_inv = num_inv * mnt_inv
  
  # final wealth
  nav_line = nav_data[cnt - 1].split(',')[1:]
  fund_nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
  for f in sorted(fund_nav_dict):
    print f, fund_nav_dict[f]
  wealth = get_wealth(fund_nav_dict, units_dict_overall)

  # absolute and annualized return
  abs_return = {}
  ann_return = {}
  last_date = nav_data[cnt - 1].split(',')[0]
  dt = datetime.strptime(last_date, '%d-%m-%Y')
  for fund in fund_names:
    cf = (dt, wealth[fund])
    cashflows_overall[fund].append(cf)
    abs_return[fund] = ((wealth[fund] / total_inv) - 1) * 100.0
    ann_return[fund] = financial.xirr(cashflows_overall) * 100.0
    print '%s, %r, %r' % (fund, abs_return[fund], ann_return[fund])
  
  pass
  
  
  # # extract the data for each fund and process them independently
  # fund_data = []
  # num_cols = len(nav_data[0].split(','))
  # for c in range(1, num_cols):
    # del fund_data[:]
    # num_rows = len(nav_data)
    # for r in range(0, num_rows):
      # row_data = nav_data[r].split(',')
      # data_tup = (row_data[0], row_data[c])
      # fund_data.append(data_tup)
    # fundStats(fund_data)
  pass

def main():
  script, nav_file = sys.argv
  nav_data = sharpeRanking.read_from_file(nav_file)
  stats(nav_data)
  pass

if __name__ == '__main__':
  main()