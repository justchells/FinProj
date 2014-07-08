#!/usr/bin/python

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
import numpy
import common
import financial
import sharpeRanking
from datetime import datetime

data_dir = 'data/rs'
mnt_inv = 1000
rf_rate_halfyr = 4.5
rf_rate_annual = 9.0

def get_wealth(nav_dict, units_dict):
  wealth = {}
  for fund in units_dict:
    wealth[fund] = float(nav_dict[fund]) * float(units_dict[fund])
  return wealth

def stats(nav_data):
  
  # create data directory
  common.create_dir(data_dir)
  
  # remove the first 12 entries in nav_data array 
  # to compare result with benchmark
  del nav_data[1:13]

  # retrieve fund names from the header row in nav_data
  # the first column (date) is skipped
  fund_names = nav_data[0].split(',')[1:]
  
  # initialize cashflows array
  cashflows = []
  
  # initialize units dictionary
  units_dict_halfyr = common.init_dict(fund_names)
  units_dict_annual = common.init_dict(fund_names)
  units_dict_overall = common.init_dict(fund_names)

  # initialize returns array
  halfyr_returns = common.init_array_dict(fund_names)
  annual_returns = common.init_array_dict(fund_names)
  
  # initialize stats array
  perf_stats = common.init_dict(fund_names)
  
  returns_absolute = common.init_dict(fund_names)
  annual_returnsized = common.init_dict(fund_names)
  returns_stats_halfyr = common.init_array_dict(fund_names)
  returns_stats_annual = common.init_array_dict(fund_names)
  
  # remove header line
  del nav_data[0]

  # compute cashflows and returns
  print 'computing cashflows and returns ...',
  cnt = len(nav_data)
  for i in range(0, cnt):
    nav_line = nav_data[i].split(',')
    dt = datetime.strptime(nav_line[0], '%d-%m-%Y')
    
    # half-yearly returns for each fund
    if i % 6 == 0 and i > 0:
      nav_line = nav_data[i].split(',')[1:]
      fund_nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
      wealth = get_wealth(fund_nav_dict, units_dict_halfyr)
      for fund in fund_names:
        cashflows_halfyr = cashflows[i-6:i]
        cf = (dt, wealth[fund])
        cashflows_halfyr.append(cf)
        ret = financial.xirr(cashflows_halfyr) * 100.0
        halfyr_returns[fund].append(ret)
      units_dict_halfyr = common.init_dict(fund_names)

    # annual returns for each fund
    if i % 12 == 0 and i > 0:
      nav_line = nav_data[i].split(',')[1:]
      fund_nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
      wealth = get_wealth(fund_nav_dict, units_dict_annual)
      for fund in fund_names:
        cashflows_annual = cashflows[i-12:i]
        cf = (dt, wealth[fund])
        cashflows_annual.append(cf)
        ret = financial.xirr(cashflows_annual) * 100.0
        annual_returns[fund].append(ret)
      units_dict_annual = common.init_dict(fund_names)
    
    # no investment on the last date
    if i == cnt - 1:
      break
    
    # invested units
    num_cols = len(nav_line)
    for j in range(1, num_cols):
      fund = fund_names[j - 1]
      nav = float(nav_line[j])
      units = mnt_inv / nav
      units_dict_halfyr[fund] += units
      units_dict_annual[fund] += units
      units_dict_overall[fund] += units
    
    # cash outflow
    cf = (dt, -mnt_inv)
    cashflows.append(cf)
  print 'done'
  
  # total investment
  num_inv = len(cashflows)
  total_inv = num_inv * mnt_inv
  
  # final wealth
  nav_line = nav_data[cnt - 1].split(',')[1:]
  fund_nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
  wealth = get_wealth(fund_nav_dict, units_dict_overall)
  
  # performance stats
  print 'generating performance stats ...',
  returns_absolute = {}
  annual_returnsized = {}
  last_date = nav_data[cnt - 1].split(',')[0]
  dt = datetime.strptime(last_date, '%d-%m-%Y')
  for fund in fund_names:
    cashflows_overall = cashflows[:]
    cf = (dt, wealth[fund])
    cashflows_overall.append(cf)
    abs_return = ((wealth[fund] / total_inv) - 1) * 100.0
    ann_return = financial.xirr(cashflows_overall) * 100.0
    
    hfr = halfyr_returns[fund]
    halfyr_return_mean = numpy.mean(hfr)
    halfyr_return_std = numpy.std(hfr)
    halfyr_sharpe = sharpeRanking.get_sharpe_ratio(hfr, rf_rate_halfyr)

    afr = annual_returns[fund]
    annual_return_mean = numpy.mean(afr)
    annual_return_std = numpy.std(afr)
    annual_sharpe = sharpeRanking.get_sharpe_ratio(afr, rf_rate_annual)
    
    perf_stats[fund] = (total_inv, wealth[fund], abs_return, ann_return, halfyr_return_mean, halfyr_return_std, halfyr_sharpe, annual_return_mean, annual_return_std, annual_sharpe)
  print 'done'
  
  print 'writing performance stats to file ...'
  sdf
  

def main():
  script, nav_file = sys.argv
  nav_data = sharpeRanking.read_from_file(nav_file)
  stats(nav_data)
  pass

if __name__ == '__main__':
  main()