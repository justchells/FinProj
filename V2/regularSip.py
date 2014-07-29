#!/usr/bin/python

import os
import common
from collections import defaultdict
from datetime import datetime

output_dir = 'output'
output_file = 'regularSip.csv'

nav_data = []
header = None
fund_names = []
num_rows = None

perf_dict = defaultdict()
risk_dict = defaultdict(float)

def set_global_vars():
  global nav_data, header, fund_names, num_rows
  nav_data = common.get_nav_data()
  header = nav_data[0]  
  fund_names = header.split(',')[1:]
  num_rows = len(nav_data)

def get_fund_nav_dict(nav_line):
  nav_dict = {}
  for fund, nav in zip(fund_names, nav_line):
    nav_dict[fund] = float(nav)
  return nav_dict
  
def compute_returns():

  inv_dict = defaultdict(float)
  units_dict = defaultdict(float)
  cashflows_dict = defaultdict(list)
  
  for i,r in enumerate(nav_data):
    
    if i < 13 or i == (num_rows - 1): continue
    dt = datetime.strptime(r.split(',')[0], '%d-%m-%Y')
    nav_line = r.split(',')[1:]
    nav_dict = get_fund_nav_dict(nav_line)
    
    cf = (dt, -common.mnt_inv)
    for fund in fund_names:
      nav = nav_dict[fund]
      units = common.mnt_inv / nav
      inv_dict[fund] += common.mnt_inv
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

def compute_sharpe():
  
  inv_dict = defaultdict(list)
  ret_dict = defaultdict(list)
  units_dict = defaultdict(list)
  
  for i,r in enumerate(nav_data):
    
    if i < 13 or i == (num_rows - 1): continue
    nav_line = r.split(',')[1:]
    nav_dict = get_fund_nav_dict(nav_line)
    
    for fund in fund_names:
      nav = nav_dict[fund]
      units = common.mnt_inv / nav
      units_dict[fund].append(units)
      inv_dict[fund].append(common.mnt_inv)
      
      if len(inv_dict[fund]) == 13:
        inv = inv_dict[fund][0]
        units = units_dict[fund][0]
        wealth = nav * units
        ret = (wealth / inv) - 1.0
        ret_dict[fund].append(ret)
        del inv_dict[fund][0]
        del units_dict[fund][0]
        
  for fund in fund_names:
    sharpe = common.get_sharpe(ret_dict[fund])
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
    
    # if fund == 'ICICIPru_Dynamic_Plan':
      # print '%d,%d,%.2f,%.2f,%.2f' % (investment, wealth, abs_return * 100.0, ann_return * 100.0, sharpe)
  
  out_file = os.path.join(output_dir, output_file)
  common.write_to_file(out_file, file_data)
    
def run():

  set_global_vars()
  compute_returns()
  compute_sharpe()
  save()
  