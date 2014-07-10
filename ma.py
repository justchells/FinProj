#!/usr/bin/python

import os
import sys
import numpy
import common
from datetime import datetime

default_inv = 1000
increment = default_inv * 10 / 100.0
min_inv = 0
max_inv = default_inv * 2
data_dir = 'data'

def get_ma_data(nav_data):
  fund_names = nav_data[0].split(',')[1:]
  num_funds = len(fund_names)

  ma_data = common.init_array_dict(fund_names)
  fund_rolling_nav = common.init_array_dict(fund_names)
  num_rows = len(nav_data)
  for i in xrange(1, num_rows):
    nav_line = nav_data[i].split(',')[1:]
    for j in xrange(0, num_funds):
      fund = fund_names[j]
      if len(fund_rolling_nav[fund]) == 6:
        ma_data[fund].append(numpy.mean(fund_rolling_nav[fund]))
        fund_rolling_nav[fund].pop(0)
      fund_rolling_nav[fund].append(float(nav_line[j]))
  return ma_data

def get_mnt_inv(ma_type, prev_inv, nav, ma):
  mnt_inv = 0
  if ma_type == 'normal':
    if ma < nav:
      mnt_inv = min(prev_inv + increment, max_inv)
    else:
      mnt_inv = max(prev_inv - increment, min_inv)
  else:
    if ma > nav:
      mnt_inv = min(prev_inv + increment, max_inv)
    else:
      mnt_inv = max(prev_inv - increment, min_inv)
  return mnt_inv
  
def run(nav_file, ma_type):
  nav_data = common.read_from_file(nav_file)
  fund_names = nav_data[0].split(',')[1:]
  del nav_data[1:7]
  ma_data = get_ma_data(nav_data)
  del nav_data[0:7]
  
  cashflows = common.init_array_dict(fund_names)
  fund_inv_dict = common.init_dict(fund_names)
  last_inv_dict = common.init_dict(fund_names, default_inv)
  units_dict_overall = common.init_dict(fund_names)
  
  cnt = len(nav_data)
  for i in xrange(0, cnt):
  
    row_data = nav_data[i].split(',')
    dt = datetime.strptime(row_data[0], '%d-%m-%Y')
    fund_nav = row_data[1:]
    fund_nav_dict = common.get_fund_nav_dict(fund_names, fund_nav)
    
    # no investment on the last date
    if i == cnt - 1:
      break
    
    for f in fund_names:
      prev_inv = last_inv_dict[f]
      nav = fund_nav_dict[f]
      ma = ma_data[f][i]
      
      mnt_inv = get_mnt_inv(ma_type, prev_inv, nav, ma)
      units = mnt_inv / nav
      
      last_inv_dict[f] = mnt_inv
      fund_inv_dict[f] += mnt_inv
      units_dict_overall[f] += units
      cf = (dt, -mnt_inv)
      cashflows[f].append(cf)
      
  file_data = []
  
  header_line = 'Fund,Investment,Wealth,Absolute Return,Annualized Return'
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
    
    line_data = \
      fund + ',' + str(fund_inv) + ',' + str(wealth[fund]) + ',' + \
      str(abs_return) + ',' + str(ann_return)
    file_data.append(line_data)
  
  ma_file_name = 'ma_' + ma_type + '.csv'
  ma_file = os.path.join(data_dir, ma_file_name)
  common.write_to_file(ma_file, file_data)
  
def main():
  script, nav_file, ma_type = sys.argv
  run(nav_file, ma_type)
  pass
  
if __name__ == '__main__':
  main()