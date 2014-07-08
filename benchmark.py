#!/usr/bin/python

import common
import numpy
import sys
import financial
import sharpeRanking
from datetime import datetime

mnt_inv = 1000

def get_wealth(nav_dict, units_dict):
  """
  Calculates the portfolio value by multiplying units invested 
  in each fund with its corresponding nav.
  """
  wealth = 0.0
  for fund in units_dict:
    wealth += float(nav_dict[fund]) * float(units_dict[fund])
  return wealth
  
def stats(nav_data, rank_data):
  """
  Generates return statistics based on sharpe ratio ranking data.
  """
  
  # remove redundant entries in nav_data
  target_date = rank_data[1].split(',')[0]
  common.trim_data(nav_data, target_date)

  # retrieve fund names
  fund_names = nav_data[0].split(',')[1:]

  # initialize units dictionary
  units_dict_halfyr = common.init_dict(fund_names, 0)
  units_dict_annual = common.init_dict(fund_names, 0)
  units_dict_overall = common.init_dict(fund_names, 0)
    
  # initialize cashflows array
  cashflows_halfyr = []
  cashflows_annual = []
  cashflows_overall = []
  
  # initialize returns array
  returns_halfyr = []
  returns_annual = []
  
  # remove header line
  del nav_data[0]
  del rank_data[0] 

  # compute cashflows and returns
  cnt = len(nav_data)
  for i in range(0, cnt):
  
    (date, fund, nav) = rank_data[i].split(',')
    dt = datetime.strptime(date, '%d-%m-%Y')
  
    # compute returns every 6 months
    if i % 6 == 0 and i > 0:
      nav_line = nav_data[i].split(',')[1:]
      nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
      wealth = get_wealth(nav_dict, units_dict_halfyr)
      cf = (dt, wealth)
      cashflows_halfyr.append(cf)
      ret = financial.xirr(cashflows_halfyr) * 100.0
      returns_halfyr.append(ret)
      del cashflows_halfyr[:]
      for f in units_dict_halfyr:
        units_dict_halfyr[f] = 0
      
    # compute returns every year
    if i % 12 == 0 and i > 0:
      nav_line = nav_data[i].split(',')[1:]
      nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
      wealth = get_wealth(nav_dict, units_dict_annual)
      cf = (dt, wealth)
      cashflows_annual.append(cf)
      ret = financial.xirr(cashflows_annual) * 100.0
      returns_annual.append(ret)
      del cashflows_annual[:]
      for f in units_dict_annual:
        units_dict_annual[f] = 0
    
    # No investment on the last date
    if i == cnt - 1:
      break
    
    # units invested
    units = mnt_inv / float(nav)
    units_dict_halfyr[fund] += units
    units_dict_annual[fund] += units
    units_dict_overall[fund] += units

    # cash outflow
    cf = (dt, -mnt_inv)
    cashflows_halfyr.append(cf)
    cashflows_annual.append(cf)
    cashflows_overall.append(cf)
  
  # total investment amount
  num_inv = len(nav_data) - 1
  total_inv = num_inv * mnt_inv
  
  # final wealth
  nav_line = nav_data[cnt - 1].split(',')[1:]
  fund_nav_dict = common.get_fund_nav_dict(fund_names, nav_line)
  wealth = get_wealth(fund_nav_dict, units_dict_overall)
  
  # absolute return
  abs_return = ((wealth / total_inv) - 1) * 100.0
  
  # annualized return
  last_date = nav_data[cnt - 1].split(',')[0]
  dt = datetime.strptime(last_date, '%d-%m-%Y')
  cf = (dt, wealth)
  cashflows_overall.append(cf)
  annual_return = financial.xirr(cashflows_overall) * 100.0

  print '\n'
  print 'Final Investment'
  print '----------------'
  for f in units_dict_overall:
    if units_dict_overall[f] > 0:
      print f, round(units_dict_overall[f], 2)
  
  print '\n'
  print 'Performance Measures'
  print '--------------------'
  print 'Investment | %s' % "{:,}".format(total_inv)  
  print 'Wealth | %s' % "{:,}".format(int(round(wealth)))
  print 'Absolute return | %s%%' % round(abs_return, 2)
  print 'Annual return | %s%%' % round(annual_return, 2)
  print '\n'

  rf_rate_halfyr = 4.5
  rf_rate_annual = 9.0
  
  print 'Half-Yearly Returns'
  print '-------------------'
  print ''
  for r in returns_halfyr:
    print '%s%%' % round(r, 2)
  print ''
  print 'Number of data points | %d' % len(returns_halfyr)
  print 'Average | %s%%' % round(numpy.mean(returns_halfyr), 2)
  print 'Standard Deviation | %s%%' % round(numpy.std(returns_halfyr), 2)
  print 'Sharpe Ratio | %r' % round(sharpeRanking.get_sharpe_ratio(returns_halfyr, rf_rate_halfyr), 2)
  print '\n'

  print 'Annual Returns'
  print '--------------'
  print ''
  for r in returns_annual:
    print '%s%%' % round(r, 2)
  print ''
  print 'Number of data points | %d' % len(returns_annual)
  print 'Average | %s%%' % round(numpy.mean(returns_annual), 2)
  print 'Standard Deviation | %s%%' % round(numpy.std(returns_annual), 2)
  print 'Sharpe Ratio | %r' % round(sharpeRanking.get_sharpe_ratio(returns_annual, rf_rate_annual), 2)
  print '\n'
  
def main():
  """
  Defined for command line. 
  Reads the file contents and calls stats().
  """
  script, nav_file, sharpe_rank_file = sys.argv
  nav_data = sharpeRanking.read_from_file(nav_file)
  rank_data = sharpeRanking.read_from_file(sharpe_rank_file)
  stats(nav_data, rank_data)
  
if __name__ == '__main__':
  main()