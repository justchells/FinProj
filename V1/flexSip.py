#!/usr/bin/python

import os
import sys
import numpy
import common
from datetime import datetime

default_inv = 1000
data_dir = 'data'
flex_stp_file_name = 'flexStp.csv'

def run(nav_file):
  
  # create data directory
  common.create_dir(data_dir)

  # read nav data
  nav_data = common.read_from_file(nav_file)
  
  # remove first 12 entries in nav_data
  # to compare results with benchmark
  del nav_data[1:13]
  
  # retrieve fund names
  # the first column (date) is skipped
  fund_names = nav_data[0].split(',')[1:]

  # initialize
  cashflows = common.init_array_dict(fund_names)
  fund_inv_dict = common.init_dict(fund_names)
  returns_halfyr = common.init_array_dict(fund_names)
  returns_annual = common.init_array_dict(fund_names)
  units_dict_halfyr = common.init_dict(fund_names)
  units_dict_annual = common.init_dict(fund_names)
  units_dict_overall = common.init_dict(fund_names)
  
  # remove header line
  del nav_data[0]
  
  cnt = len(nav_data)
  max_inv = default_inv * (cnt - 1)
  for i in range(0, cnt):
  
    row_data = nav_data[i].split(',')
    dt = datetime.strptime(row_data[0], '%d-%m-%Y')
    fund_nav = row_data[1:]
    fund_nav_dict = common.get_fund_nav_dict(fund_names, fund_nav)
      
    # half-yearly returns for each fund
    if i % 6 == 0 and i > 0:
      wealth = common.get_fund_wealth(fund_nav_dict, units_dict_halfyr)
      for fund in fund_names:
        cashflows_halfyr = cashflows[fund][i-6:i] # slice last 6 months cashflows
        cf = (dt, wealth[fund])
        cashflows_halfyr.append(cf)
        ret = common.xirr(cashflows_halfyr)
        returns_halfyr[fund].append(ret)

      # clean up for next pass
      units_dict_halfyr = common.init_dict(fund_names)
    
    # annual returns for each fund
    if i % 12 == 0 and i > 0:
      wealth = common.get_fund_wealth(fund_nav_dict, units_dict_annual)
      for fund in fund_names:
        cashflows_annual = cashflows[fund][i-12:i] # slice last 12 months cashflows
        cf = (dt, wealth[fund])
        cashflows_annual.append(cf)
        ret = common.xirr(cashflows_annual)
        returns_annual[fund].append(ret)
      
      # clean up for next pass
      units_dict_annual = common.init_dict(fund_names)
    
    # no investment on the last date
    if i == cnt - 1:
      break
    
    # portfolio value
    wealth = common.get_fund_wealth(fund_nav_dict, units_dict_overall)
    
    # units and cashflows
    for fund in fund_names:
      nav = fund_nav_dict[fund]
      fund_value = wealth[fund]
      fund_inv = fund_inv_dict[fund]
      
      # flex stp formula for calculating monthly investment
      mnt_inv = max(default_inv, default_inv * (i + 1) - fund_value)
      mnt_inv = min(mnt_inv, max_inv - fund_inv)
      fund_inv_dict[fund] += mnt_inv
      
      units = mnt_inv / nav
      units_dict_halfyr[fund] += units
      units_dict_annual[fund] += units
      units_dict_overall[fund] += units
      cf = (dt, -mnt_inv)
      cashflows[fund].append(cf)

  file_data = []
  
  header_line = \
    'Fund,Investment,Wealth,Absolute Return,Annualized Return,' + \
    'Half-Yr Return Mean,Half-Yr Return Std Dev,Half-Yr Sharpe,' + \
    'Annual Return Mean,Annual Return Std Dev,Annual Sharpe'
  file_data.append(header_line)
  
  # final wealth
  nav_line = nav_data[cnt - 1].split(',')[1:]
  fund_nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
  wealth = common.get_fund_wealth(fund_nav_dict, units_dict_overall)
  
  # performance stats for each fund
  last_date = nav_data[cnt - 1].split(',')[0]
  dt = datetime.strptime(last_date, '%d-%m-%Y')
  for fund in sorted(fund_names):  
    fund_cashflows = cashflows[fund][:]
    cf = (dt, wealth[fund])
    fund_cashflows.append(cf)
    fund_inv = fund_inv_dict[fund]
    abs_return = ((wealth[fund] / fund_inv) - 1)
    ann_return = common.xirr(fund_cashflows)

    hfr = returns_halfyr[fund]
    halfyr_rf_rate = common.get_rf_rate('half-yearly')
    halfyr_return_mean = numpy.mean(hfr)
    halfyr_return_std = numpy.std(hfr)
    halfyr_sharpe = common.get_sharpe_ratio(hfr, halfyr_rf_rate)

    afr = returns_annual[fund]
    annual_rf_rate = common.get_rf_rate('annual')
    annual_return_mean = numpy.mean(afr)
    annual_return_std = numpy.std(afr)
    annual_sharpe = common.get_sharpe_ratio(afr, annual_rf_rate)
  
    line_data = \
      fund + ',' + str(fund_inv) + ',' + str(wealth[fund]) + ',' + \
      str(abs_return) + ',' + str(ann_return) + ',' + \
      str(halfyr_return_mean) + ',' + str(halfyr_return_std) + ',' + \
      str(halfyr_sharpe) + ',' + str(annual_return_mean) + ',' + \
      str(annual_return_std) + ',' + str(annual_sharpe)
    file_data.append(line_data)
  
  flex_stp_file = os.path.join(data_dir, flex_stp_file_name)
  common.write_to_file(flex_stp_file, file_data)
  
      
def main():
  script, nav_file = sys.argv
  run(nav_file)

  
if __name__ == '__main__':
  main()
  
