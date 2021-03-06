#!/usr/bin/python

import os
import numpy
import common
from collections import defaultdict
from datetime import datetime

type = None
period = None
num_rows = None
nav_data = None
fund_names = None

inc_factor = 0.25
max_factor = 2.0

ma_dict = None
stats_dict = None
units_save_dict = None

def set_global_vars(t, p):
  
  global type, period
  type = t
  period = p
  
  global nav_data, num_rows, fund_names
  nav_data = common.get_nav_data()
  num_rows = len(nav_data)
  fund_names = nav_data[0].split(',')[1:]

  global ma_dict, stats_dict, units_save_dict
  ma_dict = defaultdict(list)
  stats_dict = defaultdict(list)
  units_save_dict = defaultdict(list)
  
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
    
    if i < (13 - period) or (i + period) >= num_rows: continue
    nav_rows = nav_data[i:i+period]
    nav_dict = get_fund_navlist_dict(fund_names, nav_rows)
    
    for fund in fund_names:
    
      nav_list = nav_dict[fund]
      avg = numpy.mean(nav_list)
      ma_dict[fund].append(avg)

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

  global stats_dict, units_save_dict
  stop_inv_dict = defaultdict(lambda: None)
  inv_dict = defaultdict(float)
  last_inv_dict = defaultdict(lambda: common.mnt_inv)
  units_dict = defaultdict(float)
  cashflows_dict = defaultdict(list)
  
  # why (num_rows - 14)
  # ignore header, first 12 rows and last row
  max_total_inv = common.mnt_inv * (num_rows - 14)
  
  for i,r in enumerate(nav_data):
    
    if i < 13 or i == (num_rows - 1): continue
    dt = datetime.strptime(r.split(',')[0], '%d-%m-%Y')
    nav_line = r.split(',')[1:]
    nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
    index = i - 13
    
    for fund in fund_names:
    
      nav = nav_dict[fund]
      ma = ma_dict[fund][i - 13]
      fund_inv = inv_dict[fund]    
      prev_inv = last_inv_dict[fund]

      allowed_inv = max_total_inv - fund_inv
      mnt_inv = get_mnt_inv(index, nav, ma, prev_inv)
      mnt_inv = min(mnt_inv, allowed_inv)
      
      units = mnt_inv / nav
      units_dict[fund] += units
      units_save_dict[fund].append(units)
      inv_dict[fund] += mnt_inv
      last_inv_dict[fund] = mnt_inv
      
      cf = (dt, -mnt_inv)
      cashflows_dict[fund].append(cf)
      
      if fund_inv + mnt_inv == max_total_inv and not stop_inv_dict[fund]:
        stop_inv_dict[fund] = (index + 1)
  
  last_line = nav_data[num_rows - 1].split(',')
  curr_dt = datetime.strptime(last_line[0], '%d-%m-%Y')
  curr_nav_line = last_line[1:]
  curr_nav_dict = common.get_fund_nav_dict(fund_names, curr_nav_line)

  for fund in fund_names:

    investment = inv_dict[fund]
    stop_inv = stop_inv_dict[fund]
    wealth = units_dict[fund] * curr_nav_dict[fund]
    abs_return = (wealth / investment) - 1
    
    cf = (curr_dt, wealth)
    cashflows_dict[fund].append(cf)
    ann_return = common.xirr(cashflows_dict[fund])
    
    stats = [investment, wealth, abs_return, ann_return, stop_inv]
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
  header_line = 'Fund,Investment,InvPeriod,Wealth,AbsoluteReturn,AnnualizedReturn,Sharpe'
  file_data.append(header_line)
  
  for fund in sorted(fund_names):
  
    (investment, wealth, abs_return, ann_return, stop_inv, sharpe) = stats_dict[fund]
    total_period = num_rows - 14
    stop_inv = total_period if not stop_inv else stop_inv
    inv_period = stop_inv * 1.0 / total_period
    line_data = fund + ',' + str(investment) + ',' + str(inv_period) + ',' \
      + str(wealth) + ',' + str(abs_return) + ',' + str(ann_return) + ',' \
      + str(sharpe)
    file_data.append(line_data)
  
  file_name = 'ma_%s_%s_month.csv' % (type, period)
  out_file_path = os.path.join('output', file_name)
  common.write_to_file(out_file_path, file_data)
  
def run(type, period):
  
  set_global_vars(type, period)
  set_ma_data()
  compute_returns()
  compute_risk()
  save()