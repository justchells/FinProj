#!/usr/bin/python

import os
import numpy
import common
from datetime import datetime
from collections import defaultdict

data_dir = 'data'
output_dir = 'output'
output_file = 'rankedMA.csv'

rank_type = None
rank = None
index = None
mnt_inv = None
num_rows = None
nav_data = None
fund_names = None

ma_type = None
ma_period = None

inc_factor = 0.25
max_factor = 2.0

ma_dict = None
data_dict = None
sharpe_rank_data = None

perf_data = None
risk_data = None

def set_global_vars(t, r, maT, maP):

  global rank_type, rank, index, mnt_inv, num_rows, nav_data, fund_names, output_file

  rank_type = t
  rank = r
  
  global ma_type, ma_period
  ma_type = maT
  ma_period = maP
  
  if rank_type == 'top':
    index = rank - 1
  elif rank_type == 'bottom':
    index = -rank

  global ma_dict
  ma_dict = defaultdict(list)
  mnt_inv = common.mnt_inv
  nav_data = common.get_nav_data()
  num_rows = len(nav_data)
  fund_names = nav_data[0].split(',')[1:]

def get_fund_navlist_dict(fund_names, nav_data):

  fund_nav_dict = defaultdict(list)
  for n in nav_data:
    nav_line = n.split(',')[1:]
    for fund, nav in zip(fund_names, nav_line):
      fund_nav_dict[fund].append(float(nav))
  return fund_nav_dict
  
def set_ma_data():

  global ma_dict
  for i,r in enumerate(nav_data):
    
    # why (13 - period)?
    # the first 13 rows in nav_data comprise the header and 12 data rows
    # we select the first index based on the moving average period
    # for 3 months MA, we use the 10th index
    # for 6 months MA, we use the 7th index and so on
    
    if i < (13 - ma_period) or (i + ma_period) >= num_rows: continue
    nav_rows = nav_data[i:i+ma_period]
    nav_dict = get_fund_navlist_dict(fund_names, nav_rows)
    
    for fund in fund_names:
    
      nav_list = nav_dict[fund]
      avg = numpy.mean(nav_list)
      ma_dict[fund].append(avg)
  
def sort_fn(fund):  

  return data_dict[fund]

def compute_rank():

  global data_dict, sharpe_rank_data
  sharpe_data = common.get_sharpe_data()
  
  sharpe_rank_data = []
  header_line = 'Date,Fund'
  sharpe_rank_data.append(header_line)
  
  for i,r in enumerate(sharpe_data):
  
    if i == 0: continue
    dt = r.split(',')[0]
    data_line = r.split(',')[1:]
    data_dict = common.get_fund_nav_dict(fund_names, data_line)
    sorted_funds = sorted(fund_names, key=sort_fn, reverse=True)
    
    line_data = dt + ',' + sorted_funds[index]
    sharpe_rank_data.append(line_data)

  sharpe_rank_file = 'sharpeRank' + str(rank_type).capitalize() + str(rank) + '.csv'
  sharpe_rank_file_path = os.path.join(data_dir, sharpe_rank_file)
  common.write_to_file(sharpe_rank_file_path, sharpe_rank_data)
  
def save_inv_data(units_dict):
  
  inv_data = []
  header_line = 'Fund,Units'
  inv_data.append(header_line)
  for fund in sorted(units_dict):
    line_data = fund + ',' + str(units_dict[fund])
    inv_data.append(line_data)
  
  inv_data_file = 'invData' + str(rank_type).capitalize() + str(rank) + '.csv'
  inv_data_file_path = os.path.join(data_dir, inv_data_file)
  common.write_to_file(inv_data_file_path, inv_data)

def get_mnt_inv(index, nav, ma, prev_inv):
  
  default_inv = common.mnt_inv
  min_inv = 0
  
  base_inv_factor = int(index / 12)
  base_inv = default_inv * (1 + base_inv_factor)
  increment = base_inv * inc_factor
  max_inv = base_inv * max_factor
  
  # max_inv = default_inv * max_factor
  # increment = default_inv * inc_factor
  
  mnt_inv = 0
  if ma_type == 'normal':
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
  
  global perf_data
  total_inv = 0
  cashflows = []
  units_dict = defaultdict(float)
  
  max_total_inv = common.mnt_inv * (num_rows - 14)

  prev_inv = common.mnt_inv
  for i,r in enumerate(nav_data):
  
    if i < 13 or i == (num_rows - 1): continue
    dt = datetime.strptime(r.split(',')[0], '%d-%m-%Y')
    nav_line = r.split(',')[1:]
    nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
    
    index = i - 13
    j = i - 12
    fund = sharpe_rank_data[j].split(',')[1]
    nav = nav_dict[fund]
    ma = ma_dict[fund][i - 13]
    
    allowed_inv = max_total_inv - total_inv
    mnt_inv = get_mnt_inv(index, nav, ma, prev_inv)
    mnt_inv = min(mnt_inv, allowed_inv)
    
    cf = (dt, -mnt_inv)
    cashflows.append(cf)
    
    units = mnt_inv / nav
    units_dict[fund] += units
    total_inv += mnt_inv
    prev_inv = mnt_inv
    
  save_inv_data(units_dict)

  last_line = nav_data[num_rows - 1].split(',')
  curr_dt = datetime.strptime(last_line[0], '%d-%m-%Y')
  curr_nav_line = last_line[1:]
  curr_nav_dict = common.get_fund_nav_dict(fund_names, curr_nav_line)
  
  wealth = 0
  for fund in units_dict:
    wealth += units_dict[fund] * curr_nav_dict[fund]
  
  cf = (curr_dt, wealth)
  cashflows.append(cf)
  abs_return = (wealth / total_inv) - 1
  ann_return = common.xirr(cashflows)
  perf_data = (total_inv, wealth, abs_return, ann_return)

def compute_risk():
  
  global risk_data
  ret_data = []
  
  for i,r in enumerate(sharpe_rank_data):

    if i == 0 or (i + 24) >= num_rows: continue
    
    fund = r.split(',')[1]
    nav_line = nav_data[i + 12].split(',')[1:]
    nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
    nav = nav_dict[fund]
    units = mnt_inv / nav
    
    curr_nav_line = nav_data[i + 24].split(',')[1:]
    curr_nav_dict = common.get_fund_nav_dict(fund_names, curr_nav_line)
    curr_nav = curr_nav_dict[fund]
    
    wealth = units * curr_nav
    ret = (wealth / mnt_inv) - 1.0
    ret_data.append(ret)
  
  sharpe = common.get_sharpe(ret_data, 'annual')
  risk_data = sharpe

def create_out_file():

  file_data = []
  header_line = 'Rank Type,Rank,MA Type,MA Period,Investment,Wealth,Absolute Return,Annualized Return,Sharpe'
  file_data.append(header_line)
  ranked_file_path = os.path.join(output_dir, output_file)
  common.write_to_file(ranked_file_path, file_data)
  
def save():

  (total_inv, wealth, abs_return, ann_return) = perf_data
  sharpe = risk_data
  
  file_data = []
  line_data = str(rank_type).capitalize() + ',' + str(rank) + ',' \
    + str(ma_type).capitalize() + ',' + str(ma_period) + ',' \
    + str(total_inv) + ',' + str(wealth) + ',' \
    + str(abs_return) + ',' + str(ann_return) + ',' + str(sharpe)
  file_data.append(line_data)

  ranked_file_path = os.path.join(output_dir, output_file)
  common.append_to_file(ranked_file_path, file_data)
  
def run(rank_type, rank, ma_type, maPeriod):

  set_global_vars(rank_type, rank, ma_type, maPeriod)
  set_ma_data()
  compute_rank()
  compute_returns()
  compute_risk()
  save()