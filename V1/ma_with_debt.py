#!/usr/bin/python

import os
import sys
import numpy
import common
from datetime import datetime

default_inv = 1000
increment = default_inv * 10 / 100.0
min_inv = 0
max_inv = default_inv * 2
int_rate = 4.0 / (100.0 * 12)
data_dir = 'data'

def get_ma_data(nav_data):
  fund_names = nav_data[0].split(',')[1:]
  num_funds = len(fund_names)

  ma_data = common.init_array_dict(fund_names)
  fund_rolling_nav = common.init_array_dict(fund_names)
  num_rows = len(nav_data)
  for i in xrange(1, num_rows):
    nav_line = nav_data[i].split(',')[1:]
    for j in xrange(0, num_funds):
      fund = fund_names[j]
      if len(fund_rolling_nav[fund]) == 6:
        ma_data[fund].append(numpy.mean(fund_rolling_nav[fund]))
        fund_rolling_nav[fund].pop(0)
      fund_rolling_nav[fund].append(float(nav_line[j]))
  return ma_data

def get_mnt_inv(ma_type, prev_inv, nav, ma):
  mnt_inv = 0
  if ma_type == 'normal':
    if ma < nav:
      mnt_inv = min(prev_inv + increment, max_inv)
    else:
      mnt_inv = max(prev_inv - increment, min_inv)
  else:
    if ma > nav:
      mnt_inv = min(prev_inv + increment, max_inv)
    else:
      mnt_inv = max(prev_inv - increment, min_inv)
  return mnt_inv

def is_cashflow_missing(cashflows):
  if len(cashflows) == 0:
    return True
    
  for c in cashflows:
    (date, cf) = c
    if cf == 0:
      return True
  
  return False
  
def run(nav_file, ma_type):
  nav_data = common.read_from_file(nav_file)
  fund_names = nav_data[0].split(',')[1:]
  del nav_data[1:7]
  ma_data = get_ma_data(nav_data)
  del nav_data[0:7]
  
  cashflows = common.init_array_dict(fund_names)
  fund_inv_dict = common.init_dict(fund_names)
  fund_corpus_dict = common.init_dict(fund_names)
  fund_corpus_index_dict = common.init_array_dict(fund_names)
  last_inv_dict = common.init_dict(fund_names, default_inv)
  returns_halfyr = common.init_array_dict(fund_names)
  returns_annual = common.init_array_dict(fund_names)
  units_dict_halfyr = common.init_dict(fund_names)
  units_dict_annual = common.init_dict(fund_names)
  units_dict_overall = common.init_dict(fund_names)
  
  cnt = len(nav_data)
  max_total_inv = default_inv * (cnt - 1)
  for i in xrange(0, cnt):
  
    row_data = nav_data[i].split(',')
    dt = datetime.strptime(row_data[0], '%d-%m-%Y')
    fund_nav = row_data[1:]
    fund_nav_dict = common.get_fund_nav_dict(fund_names, fund_nav)
    
    # half-yearly returns for each fund
    if i % 6 == 0 and i > 0:
      
      wealth = common.get_fund_wealth(fund_nav_dict, units_dict_halfyr)
      for fund in fund_names:
        start_corpus = fund_corpus_index_dict[fund][i-7]
        end_corpus = fund_corpus_index_dict[fund][i-1]
        corpus_wealth = end_corpus - start_corpus
        total_wealth = wealth[fund] + corpus_wealth
        
        cashflows_halfyr = cashflows[fund][i-6:i] # slice last 6 months cashflows
        if is_cashflow_missing(cashflows_halfyr):
          continue
          
        cf = (dt, total_wealth)
        cashflows_halfyr.append(cf)
        ret = common.xirr(cashflows_halfyr)
        returns_halfyr[fund].append(ret)

      # clean up
      units_dict_halfyr = common.init_dict(fund_names)

    # annual returns for each fund
    if i % 12 == 0 and i > 0:
      
      wealth = common.get_fund_wealth(fund_nav_dict, units_dict_annual)
      for fund in fund_names:
        start_corpus = fund_corpus_index_dict[fund][i-13]
        end_corpus = fund_corpus_index_dict[fund][i-1]
        corpus_wealth = end_corpus - start_corpus
        total_wealth = wealth[fund] + corpus_wealth
      
        cashflows_annual = cashflows[fund][i-12:i] # slice last 12 months cashflows
        if is_cashflow_missing(cashflows_annual):
          continue
          
        cf = (dt, wealth[fund] + fund_corpus_dict[fund])
        cashflows_annual.append(cf)
        ret = common.xirr(cashflows_annual)
        returns_annual[fund].append(ret)

      # clean up
      units_dict_annual = common.init_dict(fund_names)
    
    # no investment on the last date
    if i == cnt - 1:
      break
    
    for f in fund_names:
      
      # cap total investment
      allowed_inv = max_total_inv - fund_inv_dict[f]
    
      prev_inv = last_inv_dict[f]
      nav = fund_nav_dict[f]
      ma = ma_data[f][i]
      
      # equity investment
      mnt_inv = get_mnt_inv(ma_type, prev_inv, nav, ma)
      mnt_inv = min(mnt_inv, allowed_inv)
      last_inv_dict[f] = mnt_inv
      allowed_inv -= mnt_inv
      
      # debt investment
      corpus = fund_corpus_dict[f]
      debt_inv = default_inv - mnt_inv
      if debt_inv < 0:
        debt_inv = -min(mnt_inv - default_inv, corpus)
      else:
        debt_inv = min(debt_inv, allowed_inv)
        
      # corpus investment + interest
      corpus += debt_inv
      interest = corpus * int_rate
      corpus += interest
      fund_corpus_dict[f] = corpus
      fund_corpus_index_dict[f].append(corpus)
      
      # total investment
      total_inv = mnt_inv + debt_inv
      fund_inv_dict[f] += total_inv

      # invested units
      units = mnt_inv / nav
      units_dict_overall[f] += units
      units_dict_halfyr[f] += units
      units_dict_annual[f] += units

      # cashflows
      cf = (dt, -total_inv)
      cashflows[f].append(cf)

      # debugging
      # if f == 'Birla_Advantage_Fund':
        # print '%d\t%d\t%d\t%.2f\t%d\t%d' % (mnt_inv, debt_inv, round(fund_inv_dict[f]), units, -total_inv, round(corpus))

  file_data = []
  
  header_line = \
    'Fund,Investment,Wealth,Absolute Return,Annualized Return,' + \
    'Half-Yr Return Mean,Half-Yr Return Std Dev,Half-Yr Sharpe,' + \
    'Annual Return Mean,Annual Return Std Dev,Annual Sharpe'
  file_data.append(header_line)
  
  # final wealth
  nav_line = nav_data[cnt - 1].split(',')[1:]
  fund_nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
  wealth = common.get_fund_wealth(fund_nav_dict, units_dict_overall)

  # performance stats for each fund
  last_date = nav_data[cnt - 1].split(',')[0]
  dt = datetime.strptime(last_date, '%d-%m-%Y')
  for fund in sorted(fund_names):    
    total_wealth = wealth[fund] + fund_corpus_dict[fund]
    fund_cashflows = cashflows[fund][:]
    cf = (dt, total_wealth)
    fund_cashflows.append(cf)
    
    fund_inv = fund_inv_dict[fund]
    abs_return = ((total_wealth / fund_inv) - 1)
    ann_return = common.xirr(fund_cashflows)
    
    hfr = returns_halfyr[fund]
    halfyr_rf_rate = common.get_rf_rate('half-yearly')
    halfyr_return_mean = numpy.mean(hfr)
    halfyr_return_std = numpy.std(hfr)
    halfyr_sharpe = common.get_sharpe_ratio(hfr, halfyr_rf_rate)

    afr = returns_annual[fund]
    annual_rf_rate = common.get_rf_rate('annual')
    annual_return_mean = numpy.mean(afr)
    annual_return_std = numpy.std(afr)
    annual_sharpe = common.get_sharpe_ratio(afr, annual_rf_rate)
  
    line_data = \
      fund + ',' + str(fund_inv) + ',' + str(total_wealth) + ',' + \
      str(abs_return) + ',' + str(ann_return) + ',' + \
      str(halfyr_return_mean) + ',' + str(halfyr_return_std) + ',' + \
      str(halfyr_sharpe) + ',' + str(annual_return_mean) + ',' + \
      str(annual_return_std) + ',' + str(annual_sharpe)
    file_data.append(line_data)
  
  ma_file_name = 'ma_with_debt_' + ma_type + '.csv'
  ma_file = os.path.join(data_dir, ma_file_name)
  common.write_to_file(ma_file, file_data)
  
def main():
  script, nav_file, ma_type = sys.argv
  run(nav_file, ma_type)
  pass
  
if __name__ == '__main__':
  main()