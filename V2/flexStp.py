#!/usr/bin/python

import os
import common
from collections import defaultdict
from datetime import datetime

num_rows = None
nav_data = None
fund_names = None

stats_dict = defaultdict(list)
units_save_dict = defaultdict(list)

def set_global_vars():

  global nav_data, fund_names, num_rows
  nav_data = common.get_nav_data()
  fund_names = nav_data[0].split(',')[1:]
  num_rows = len(nav_data)

def get_fund_wealth(units_dict, nav_dict):

  fund_wealth = defaultdict(float)
  for fund in units_dict:
    fund_wealth[fund] = units_dict[fund] * nav_dict[fund]
  return fund_wealth
  
def compute_returns():
  
  global stats_dict, units_save_dict
  inv_dict = defaultdict(float)
  units_dict = defaultdict(float)
  cashflows_dict = defaultdict(list)
  
  default_inv = common.mnt_inv
  max_inv = default_inv * (num_rows - 14)

  for i,r in enumerate(nav_data):
    
    if i < 13 or i == (num_rows - 1): continue
    dt = datetime.strptime(r.split(',')[0], '%d-%m-%Y')
    nav_line = r.split(',')[1:]
    nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
    wealth = get_fund_wealth(units_dict, nav_dict)
    
    index = i - 12
    for fund in fund_names:
    
      nav = nav_dict[fund]
      fund_value = wealth[fund]
      fund_inv = inv_dict[fund]
      
      mnt_inv = max(default_inv, default_inv * index - fund_value)
      mnt_inv = min(mnt_inv, max_inv - fund_inv)
      inv_dict[fund] += mnt_inv
      
      units = mnt_inv / nav
      units_dict[fund] += units
      units_save_dict[fund].append(units)
      cf = (dt, -mnt_inv)
      cashflows_dict[fund].append(cf)
    
  last_line = nav_data[num_rows - 1].split(',')
  curr_dt = datetime.strptime(last_line[0], '%d-%m-%Y')
  curr_nav_line = last_line[1:]
  curr_nav_dict = common.get_fund_nav_dict(fund_names, curr_nav_line)

  for fund in fund_names:
    
    investment = inv_dict[fund]
    wealth = units_dict[fund] * curr_nav_dict[fund]
    abs_return = (wealth / investment) - 1
    
    cf = (curr_dt, wealth)
    cashflows_dict[fund].append(cf)
    ann_return = common.xirr(cashflows_dict[fund])
    
    stats = [investment, wealth, abs_return, ann_return]
    stats_dict[fund].extend(stats)
  
def compute_risk():

  global stats_dict
  for fund in fund_names:
    
    ret_data = []
    for i, units in enumerate(units_save_dict[fund]):
    
      # why (i + 13) and (i + 25)?
      # the header row and first 12 rows are ignored in nav_data
      # hence, the first index where investment starts is (i + 13)
      # to look nav of this investment one year later, we use (i + 25)
    
      if (i + 25) >= num_rows: break
      
      nav_line = nav_data[i + 13].split(',')[1:]
      nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
      inv = units * nav_dict[fund]
      if inv == 0: continue
      
      curr_nav_line = nav_data[i + 25].split(',')[1:]
      curr_nav_dict = common.get_fund_nav_dict(fund_names, curr_nav_line)
      wealth = units * curr_nav_dict[fund]
      
      ret = (wealth / inv) - 1.0
      ret_data.append(ret)
    
    sharpe = common.get_sharpe(ret_data, 'annual')
    stats_dict[fund].append(sharpe)

def save():

  file_data = []
  header_line = 'Fund,Investment,Wealth,AbsoluteReturn,AnnualizedReturn,Sharpe'
  file_data.append(header_line)
  
  for fund in sorted(fund_names):
  
    (investment, wealth, abs_return, ann_return, sharpe) = stats_dict[fund]
    line_data = fund + ',' + str(investment) + ',' + str(wealth) + ',' \
      + str(abs_return) + ',' + str(ann_return) + ',' + str(sharpe)
    file_data.append(line_data)
    
  out_file_path = os.path.join('output', 'flexStp.csv')
  common.write_to_file(out_file_path, file_data)
  
def run():
  set_global_vars()
  compute_returns()
  compute_risk()
  save()