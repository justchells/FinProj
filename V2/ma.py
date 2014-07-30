#!/usr/bin/python

import os
import numpy
import common
from collections import defaultdict
from datetime import datetime

out_dir = 'output'
out_file = None

type = None
period = None
num_rows = None
nav_data = None
fund_names = None

min_inv = None
max_inv = None
increment = None

ma_dict = defaultdict(list)
perf_dict = defaultdict()

inc_factor = 0.10
max_factor = 2.0

def set_global_vars(t, p):
  
  global type, period, nav_data, num_rows, fund_names
  type = t
  period = p
  nav_data = common.get_nav_data()
  num_rows = len(nav_data)
  fund_names = nav_data[0].split(',')[1:]

def get_fund_nav_dict(fund_names, nav_data):
  fund_nav_dict = defaultdict(list)
  for n in nav_data:
    nav_line = n.split(',')[1:]
    for fund, nav in zip(fund_names, nav_line):
      fund_nav_dict[fund].append(float(nav))
  return fund_nav_dict
  
def set_ma_data():

  global ma_dict
  for i,r in enumerate(nav_data):
    
    if i < (13 - period) or (i + period) >= num_rows: continue
    nav_rows = nav_data[i:i+period]
    nav_dict = get_fund_nav_dict(fund_names, nav_rows)
    
    for fund in fund_names:
    
      nav_list = nav_dict[fund]
      avg = numpy.mean(nav_list)
      ma_dict[fund].append(avg)
  pass

def get_mnt_inv(nav, ma, prev_inv):
  
  mnt_inv = 0
  if type == 'normal':
    if nav > ma:
      mnt_inv = min(prev_inv + increment, max_inv)
    else:
      mnt_inv = max(prev_inv - increment, min_inv)
  else:
    if nav < ma:
      mnt_inv = min(prev_inv + increment, max_inv)
    else:
      mnt_inv = max(prev_inv - increment, min_inv)
  return mnt_inv
  
def compute_returns():

  global min_inv, max_inv, increment
  default_inv = common.mnt_inv
  min_inv = 0
  max_inv = default_inv * max_factor
  increment = default_inv * inc_factor
  max_total_inv = default_inv * (num_rows - 14)
  

  global perf_dict
  inv_dict = defaultdict(float)
  last_inv_dict = defaultdict(lambda: default_inv)
  units_dict = defaultdict(float)
  cashflows_dict = defaultdict(list)
  
  for i,r in enumerate(nav_data):
    
    if i < 13 or i == (num_rows - 1): continue
    dt = datetime.strptime(r.split(',')[0], '%d-%m-%Y')
    nav_line = r.split(',')[1:]
    nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
    
    for fund in fund_names:
    
      nav = nav_dict[fund]
      ma = ma_dict[fund][i - 13]
      fund_inv = inv_dict[fund]    
      prev_inv = last_inv_dict[fund]

      allowed_inv = max_total_inv - fund_inv
      mnt_inv = get_mnt_inv(nav, ma, prev_inv)
      mnt_inv = min(mnt_inv, allowed_inv)
      
      units = mnt_inv / nav
      units_dict[fund] += units
      inv_dict[fund] += mnt_inv
      last_inv_dict[fund] = mnt_inv
      
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
  
def run(type, period):
  
  set_global_vars(type, period)
  set_ma_data()
  compute_returns()
  compute_risk()
  save()