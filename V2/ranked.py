#!/usr/bin/python

import os
import common
from datetime import datetime
from collections import defaultdict

data_dir = 'data'
output_dir = 'output'
output_file = 'ranked.csv'

type = None
rank = None
index = None
mnt_inv = None
num_rows = None
nav_data = None
fund_names = None

data_dict = None
sharpe_rank_data = None

perf_data = None
risk_data = None

def set_global_vars(t, r):

  global type, rank, index, mnt_inv, num_rows, nav_data, fund_names, output_file

  type = t
  rank = r
  
  if type == 'top':
    index = rank - 1
  elif type == 'bottom':
    index = -rank

  mnt_inv = common.mnt_inv
  nav_data = common.get_nav_data()
  num_rows = len(nav_data)
  fund_names = nav_data[0].split(',')[1:]
  
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

  sharpe_rank_file = 'sharpeRank' + str(type).capitalize() + str(rank) + '.csv'
  sharpe_rank_file_path = os.path.join(data_dir, sharpe_rank_file)
  common.write_to_file(sharpe_rank_file_path, sharpe_rank_data)
  
def save_inv_data(units_dict):
  
  inv_data = []
  header_line = 'Fund,Units'
  inv_data.append(header_line)
  for fund in sorted(units_dict):
    line_data = fund + ',' + str(units_dict[fund])
    inv_data.append(line_data)
  
  inv_data_file = 'invData' + str(type).capitalize() + str(rank) + '.csv'
  inv_data_file_path = os.path.join(data_dir, inv_data_file)
  common.write_to_file(inv_data_file_path, inv_data)
  
def compute_returns():
  
  global perf_data
  total_inv = 0
  cashflows = []
  units_dict = defaultdict(float)
  
  for i,r in enumerate(nav_data):
  
    if i < 13 or i == (num_rows - 1): continue
    dt = datetime.strptime(r.split(',')[0], '%d-%m-%Y')
    nav_line = r.split(',')[1:]
    nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
    
    total_inv += mnt_inv
    cf = (dt, -mnt_inv)
    cashflows.append(cf)
    
    j = i - 12
    fund = sharpe_rank_data[j].split(',')[1]
    nav = nav_dict[fund]
    units = mnt_inv / nav
    units_dict[fund] += units
    
  save_inv_data(units_dict)

  last_line = nav_data[num_rows - 1].split(',')
  curr_dt = datetime.strptime(last_line[0], '%d-%m-%Y')
  curr_nav_line = last_line[1:]
  
  curr_nav_dict = {}
  for fund, nav in zip(fund_names, curr_nav_line):
    curr_nav_dict[fund] = float(nav)
  
  wealth = 0
  for fund in units_dict:
    nav = curr_nav_dict[fund]
    wealth += nav * units_dict[fund]
  
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
  header_line = 'Type,Rank,Investment,Wealth,AbsoluteReturn,AnnualizedReturn,Sharpe'
  file_data.append(header_line)
  ranked_file_path = os.path.join(output_dir, output_file)
  common.write_to_file(ranked_file_path, file_data)
  
def save():

  (total_inv, wealth, abs_return, ann_return) = perf_data
  sharpe = risk_data
  
  file_data = []
  line_data = str(type) + ',' + str(rank) + ',' + str(total_inv) + ',' + \
    str(wealth) + ',' + str(abs_return) + ',' + str(ann_return) + ',' + str(sharpe)
  file_data.append(line_data)

  ranked_file_path = os.path.join(output_dir, output_file)
  common.append_to_file(ranked_file_path, file_data)
  
def run(type, rank):

  set_global_vars(type, rank)
  compute_rank()
  compute_returns()
  compute_risk()
  save()