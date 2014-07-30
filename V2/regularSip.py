#!/usr/bin/python

import os
import common
from collections import defaultdict
from datetime import datetime

output_dir = 'output'
output_file = 'regularSip.csv'

mnt_inv = None
num_rows = None
nav_data = None
fund_names = None

perf_dict = defaultdict()
risk_dict = defaultdict(float)

def set_global_vars():

  global nav_data, fund_names, num_rows, mnt_inv
  nav_data = common.get_nav_data()
  fund_names = nav_data[0].split(',')[1:]
  num_rows = len(nav_data)
  mnt_inv = common.mnt_inv

def compute_returns():

  inv_dict = defaultdict(float)
  units_dict = defaultdict(float)
  cashflows_dict = defaultdict(list)
  
  for i,r in enumerate(nav_data):
    
    if i < 13 or i == (num_rows - 1): continue
    dt = datetime.strptime(r.split(',')[0], '%d-%m-%Y')
    nav_line = r.split(',')[1:]
    nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
    
    cf = (dt, -mnt_inv)
    for fund in fund_names:
      nav = nav_dict[fund]
      units = mnt_inv / nav
      inv_dict[fund] += mnt_inv
      units_dict[fund] += units
      cashflows_dict[fund].append(cf)

  last_line = nav_data[num_rows - 1].split(',')
  curr_dt = datetime.strptime(last_line[0], '%d-%m-%Y')
  curr_nav_line = last_line[1:]
  
  curr_nav_dict = {}
  for fund, nav in zip(fund_names, curr_nav_line):
    curr_nav_dict[fund] = float(nav)

  for fund in fund_names:
    investment = inv_dict[fund]
    wealth = units_dict[fund] * curr_nav_dict[fund]
    cf = (curr_dt, wealth)
    cashflows_dict[fund].append(cf)
    abs_return = (wealth / investment) - 1
    ann_return = common.xirr(cashflows_dict[fund])
    perf_dict[fund] = (investment, wealth, abs_return, ann_return)

def compute_risk():
  
  inv_dict = defaultdict(list)
  ret_dict = defaultdict(list)
  units_dict = defaultdict(list)
  
  for i,r in enumerate(nav_data):
    
    if i < 13 or i == (num_rows - 1): continue
    nav_line = r.split(',')[1:]
    nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
    
    for fund in fund_names:
      nav = nav_dict[fund]
      units = mnt_inv / nav
      units_dict[fund].append(units)
      inv_dict[fund].append(mnt_inv)
      
      if len(inv_dict[fund]) == 13:
        inv = inv_dict[fund][0]
        units = units_dict[fund][0]
        wealth = nav * units
        ret = (wealth / inv) - 1.0
        ret_dict[fund].append(ret)
        del inv_dict[fund][0]
        del units_dict[fund][0]
        
  for fund in fund_names:
    sharpe = common.get_sharpe(ret_dict[fund], 'annual')
    risk_dict[fund] = sharpe

def save():

  file_data = []
  header_line = 'Fund,Investment,Wealth,AbsoluteReturn,AnnualizedReturn,Sharpe'
  file_data.append(header_line)
  
  for fund in fund_names:
    (investment, wealth, abs_return, ann_return) = perf_dict[fund]
    sharpe = risk_dict[fund]

    line_data = fund + ',' + str(investment) + ',' + str(wealth) + ',' \
      + str(abs_return) + ',' + str(ann_return) + ',' + str(sharpe)
    file_data.append(line_data)
    
  out_file = os.path.join(output_dir, output_file)
  common.write_to_file(out_file, file_data)
    
def run():

  set_global_vars()
  compute_returns()
  compute_risk()
  save()