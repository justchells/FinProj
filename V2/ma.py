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

def get_mnt_inv(nav, ma, prev_inv):
  
  default_inv = common.mnt_inv
  min_inv = 0
  max_inv = default_inv * max_factor
  increment = default_inv * inc_factor
  
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
      units_save_dict[fund].append(units)
      inv_dict[fund] += mnt_inv
      last_inv_dict[fund] = mnt_inv
      
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
  
  for fund in fund_names:
  
    (investment, wealth, abs_return, ann_return, sharpe) = stats_dict[fund]
    line_data = fund + ',' + str(investment) + ',' + str(wealth) + ',' \
      + str(abs_return) + ',' + str(ann_return) + ',' + str(sharpe)
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

def stats_inc_factor():
  
  global inc_factor
  max_factor = 2.0
  stat_data = []
  
  for v in xrange(0, 101):
    
    val = v / 100.0
    print 'inc_factor - %.2f' % val
    inc_factor = val
    set_global_vars('inverted', 12)
    set_ma_data()
    compute_returns()
    compute_risk()
    
    ret_data = []
    risk_data = []
    for fund in fund_names:
      (investment, wealth, abs_return, ann_return, sharpe) = stats_dict[fund]
      ret_data.append(ann_return)
      risk_data.append(sharpe)
    
    avg_ret = numpy.mean(ret_data)
    avg_risk = numpy.mean(risk_data)
    stat = '%s,%s,%s' % (inc_factor, avg_ret, avg_risk)
    stat_data.append(stat)
  
  out_file_path = os.path.join('output', 'ma_stats_inc_factor.csv')
  common.write_to_file(out_file_path, stat_data)
  
def optimize(target, factor):

  common.header('Optimizing ' + target + ' using ' + factor)

  global inc_factor, max_factor
  inc_factor = 0.25
  max_factor = 2.0
  stat_data = []

  if factor == 'inc_factor':
    min_range = 0
    max_range = 101
    div_factor = 100.0
  elif factor == 'max_factor':
    min_range = 1
    max_range = 11
    div_factor = 2.0
  
  for p in (3, 6, 9, 12):
  
    print '%d months inverted MA' % p
    max_val = 0.0
    opt_val = 0.0
    
    for v in xrange(min_range, max_range):
    
      val = v / div_factor
      if factor == 'inc_factor':
        inc_factor = val
      elif factor == 'max_factor':
        max_factor = val
      
      set_global_vars('inverted', p)
      set_ma_data()
      compute_returns()
      compute_risk()
    
      val_data = []
      for fund in fund_names:
        (investment, wealth, abs_return, ann_return, sharpe) = stats_dict[fund]
        if target == 'returns':
          val_data.append(ann_return)
        elif target == 'risk':
          val_data.append(sharpe)
      curr_val = numpy.mean(val_data)
        
      if curr_val > max_val:
        print 'improved value at %.2f - %.4f' % (val, curr_val)
        opt_val = val
        max_val = curr_val
  
    stat = '%d months MA, %.2f, %.4f' % (p, opt_val, max_val)
    stat_data.append(stat)
  
  print '\nResults'
  print '-' * 10
  print '\n'.join(stat_data)  