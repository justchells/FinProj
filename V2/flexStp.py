#!/usr/bin/python

import os
import common
from collections import defaultdict
from datetime import datetime

output_dir = 'output'
output_file = 'flexStp.csv'

num_rows = None
nav_data = None
fund_names = None
default_inv = None

perf_dict = defaultdict()
risk_dict = defaultdict(float)

def set_global_vars():

  global nav_data, fund_names, num_rows, default_inv
  nav_data = common.get_nav_data()
  fund_names = nav_data[0].split(',')[1:]
  num_rows = len(nav_data)
  default_inv = common.mnt_inv

def get_fund_wealth(units_dict, nav_dict):
  fund_wealth = defaultdict(float)
  for fund in units_dict:
    fund_wealth[fund] = units_dict[fund] * nav_dict[fund]
  return fund_wealth
  
def compute_returns():
  
  inv_dict = defaultdict(float)
  units_dict = defaultdict(float)
  cashflows_dict = defaultdict(list)
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
      cf = (dt, -mnt_inv)
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
  pass
  
def compute_risk():
  pass

def save():
  pass
  
def run():
  set_global_vars()
  compute_returns()
  compute_risk()
  save()