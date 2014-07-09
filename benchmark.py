#!/usr/bin/python

import os
import sys
import numpy
import common
from datetime import datetime

mnt_inv = 1000
data_dir = 'data'
benchmark_file_name = 'benchmark.csv'

def get_wealth(nav_dict, units_dict):
  """
  Calculates the portfolio value by multiplying units invested 
  in each fund with its corresponding nav.
  """
  
  wealth = 0.0
  for fund in units_dict:
    wealth += float(nav_dict[fund]) * float(units_dict[fund])
  return wealth
  
def run(nav_file, rank_file):
  """
  Generates return statistics based on sharpe ratio ranking data.
  """

  # create data directory
  common.create_dir(data_dir)

  # read data files
  nav_data = common.read_from_file(nav_file)
  rank_data = common.read_from_file(rank_file)
  
  # remove redundant entries in nav_data
  target_date = rank_data[1].split(',')[0]
  common.trim_data(nav_data, target_date)
  assert len(nav_data) == len(rank_data)

  # retrieve fund names
  # the first column (date) is skipped
  fund_names = nav_data[0].split(',')[1:]

  # initialize
  cashflows_halfyr = []
  cashflows_annual = []
  cashflows_overall = []
  returns_halfyr = []
  returns_annual = []
  units_dict_halfyr = common.init_dict(fund_names)
  units_dict_annual = common.init_dict(fund_names)
  units_dict_overall = common.init_dict(fund_names)

  # remove header line
  del nav_data[0]
  del rank_data[0] 

  # compute cashflows and returns
  cnt = len(nav_data)
  for i in range(0, cnt):
  
    (date, fund, nav) = rank_data[i].split(',')
    dt = datetime.strptime(date, '%d-%m-%Y')
  
    # half-yearly returns
    if i % 6 == 0 and i > 0:
      nav_line = nav_data[i].split(',')[1:]
      fund_nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
      wealth = get_wealth(fund_nav_dict, units_dict_halfyr)
      cf = (dt, wealth)
      cashflows_halfyr.append(cf)
      ret = common.xirr(cashflows_halfyr)
      returns_halfyr.append(ret)

      # clean up for next pass
      del cashflows_halfyr[:]
      units_dict_halfyr[f] = common.init_dict(fund_names)
      
    # annual returns
    if i % 12 == 0 and i > 0:
      nav_line = nav_data[i].split(',')[1:]
      nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
      wealth = get_wealth(nav_dict, units_dict_annual)
      cf = (dt, wealth)
      cashflows_annual.append(cf)
      ret = common.xirr(cashflows_annual)
      returns_annual.append(ret)

      # clean up for next pass
      del cashflows_annual[:]
      units_dict_annual[f] = common.init_dict(fund_names)
    
    # no investment on the last date
    if i == cnt - 1:
      break
    
    # units invested
    units = mnt_inv / float(nav)
    units_dict_halfyr[fund] += units
    units_dict_annual[fund] += units
    units_dict_overall[fund] += units

    # cash outflow
    cf = (dt, -mnt_inv)
    cashflows_halfyr.append(cf)
    cashflows_annual.append(cf)
    cashflows_overall.append(cf)
  
  file_data = []
  
  # investment details
  file_data.append('Investment Details')
  file_data.append('Fund,Units')
  for f in units_dict_overall:
    if units_dict_overall[f] > 0:
      line_data = f + ','  + str(units_dict_overall[f])
      file_data.append(line_data)
  file_data.append('\n')
  
  # total investment
  num_inv = len(cashflows_overall)
  total_inv = num_inv * mnt_inv
  file_data.append('Investment,' + str(total_inv))
  
  # final wealth
  nav_line = nav_data[cnt - 1].split(',')[1:]
  fund_nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
  wealth = get_wealth(fund_nav_dict, units_dict_overall)
  file_data.append('Wealth,' + str(wealth))
  
  # absolute return
  abs_return = ((wealth / total_inv) - 1)
  file_data.append('Absolute Return,' + str(abs_return))
  
  # annualized return
  last_date = nav_data[cnt - 1].split(',')[0]
  dt = datetime.strptime(last_date, '%d-%m-%Y')
  cf = (dt, wealth)
  cashflows_overall.append(cf)
  annual_return = common.xirr(cashflows_overall)
  file_data.append('Annualized Return,' + str(annual_return))
  
  file_data.append('\n')
  file_data.append('Stats,Mean,Std Deviation, Sharpe Ratio')
  
  # half-yearly return stats
  halfyr_rf_rate = common.get_rf_rate('half-yearly')
  halfyr_mean = numpy.mean(returns_halfyr)
  halfyr_stdev = numpy.std(returns_halfyr)
  halfyr_sharpe = common.get_sharpe_ratio(returns_halfyr, halfyr_rf_rate)
  file_data.append('Half-Yearly,' + str(halfyr_mean) + ',' + str(halfyr_stdev) + ',' + str(halfyr_sharpe))
  
  # annual return stats
  annual_rf_rate = common.get_rf_rate('annual')
  annual_mean = numpy.mean(returns_annual)
  annual_stdev = numpy.std(returns_annual)
  annual_sharpe = common.get_sharpe_ratio(returns_annual, annual_rf_rate)
  file_data.append('Annual,' + str(annual_mean) + ',' + str(annual_stdev) + ',' + str(annual_sharpe))
  
  # save stats to file
  benchmark_file = os.path.join(data_dir, benchmark_file_name)
  common.write_to_file(benchmark_file, file_data)

  
def main():
  script, nav_file, rank_file = sys.argv
  run(nav_file, rank_file)

  
if __name__ == '__main__':
  main()

