#!/usr/bin/python

import os
import common
from collections import defaultdict
from datetime import datetime

num_rows = None
nav_data = None
fund_names = None

stats_data = []

def set_global_vars():
  
  global nav_data, fund_names, num_rows
  nav_data = common.get_nav_data()
  fund_names = nav_data[0].split(',')[1:]
  num_rows = len(nav_data)

def compute_returns():

  global stats_data
  cashflows = []
  units_dict = defaultdict(float)
  
  num_funds = len(fund_names)
  default_inv = common.mnt_inv
  mnt_inv = (default_inv * 1.0) / num_funds
  print 'monthly investment - %f' % mnt_inv
  
  total_inv = 0
  for i,r in enumerate(nav_data):
  
    if i < 13 or i == (num_rows - 1): continue
    dt = datetime.strptime(r.split(',')[0], '%d-%m-%Y')
    nav_line = r.split(',')[1:]
    nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
    
    cf = (dt, -default_inv)
    cashflows.append(cf)
    
    for fund in fund_names:
    
      nav = nav_dict[fund]
      units = mnt_inv / nav
      units_dict[fund] += units
      total_inv += mnt_inv
      
  last_line = nav_data[num_rows - 1].split(',')
  curr_dt = datetime.strptime(last_line[0], '%d-%m-%Y')
  curr_nav_line = last_line[1:]
  curr_nav_dict = common.get_fund_nav_dict(fund_names, curr_nav_line)
  
  wealth = 0
  for fund in fund_names:
    wealth += units_dict[fund] * curr_nav_dict[fund]
  
  cf = (curr_dt, wealth)
  cashflows.append(cf)
  abs_return = (wealth / total_inv) - 1
  ann_return = common.xirr(cashflows)
  stat = [total_inv, wealth, abs_return, ann_return]
  stats_data.extend(stat)
  
def compute_risk():

  global stats_data
  num_funds = len(fund_names)
  default_inv = common.mnt_inv
  mnt_inv = default_inv / num_funds

  ret_data = []
  for i,r in enumerate(nav_data):
  
    if i < 13: continue
    if (i + 25) >= num_rows: break
    
    nav_line = nav_data[i + 13].split(',')[1:]
    nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
    
    curr_nav_line = nav_data[i + 25].split(',')[1:]
    curr_nav_dict = common.get_fund_nav_dict(fund_names, curr_nav_line)
    
    inv = default_inv
    
    wealth = 0
    for fund in fund_names:
      
      nav = nav_dict[fund]
      units = mnt_inv / nav
      wealth += units * curr_nav_dict[fund]
  
    ret = (wealth / inv) - 1.0
    ret_data.append(ret)
  
  sharpe = common.get_sharpe(ret_data, 'annual')
  stats_data.append(sharpe)
  
def save():

  file_data = []
  header_line = 'Investment,Wealth,AbsoluteReturn,AnnualizedReturn,Sharpe'
  file_data.append(header_line)

  (investment, wealth, abs_return, ann_return, sharpe) = stats_data

  line_data = str(investment) + ',' + str(wealth) + ',' + str(abs_return) \
    + ',' + str(ann_return) + ',' + str(sharpe)
  file_data.append(line_data)
  
  out_file_path = os.path.join('output', 'equalWt.csv')
  common.write_to_file(out_file_path, file_data)

def run():

  set_global_vars()
  compute_returns()
  compute_risk()
  save()