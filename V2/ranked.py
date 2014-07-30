#!/usr/bin/python

import os
import common
from collections import defaultdict

data_dir = 'data'
output_dir = 'output'
output_file = None

type = None
rank = None
index = None
mnt_inv = None
nav_data = None
fund_names = None

data_dict = None

def set_global_vars(t, r):

  global type, rank, index, mnt_inv, nav_data, fund_names, output_file

  if type == 'top':
    index = rank - 1
  elif type == 'bottom':
    index = -rank

  type = t
  rank = r
  mnt_inv = common.mnt_inv
  nav_data = common.get_nav_data()
  fund_names = nav_data[0].split(',')[1:]
  output_file = 'ranked_' + str(type) + str(rank) + '.csv'
  
def sort_fn(fund):  

  return data_dict[fund]

def compute_rank():

  global data_dict
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
  
def compute_returns():
  pass

def compute_risk():
  pass

def save():
  pass
  
def run(type, rank):

  set_global_vars(type, rank)
  compute_rank()
  compute_returns()
  compute_risk()
  save()