import numpy
import sys
import sharpeRanking
from datetime import datetime

mnt_inv = 1000

def xirr(transactions):
  """
  Code taken from stackoverflow.com - 
  http://stackoverflow.com/a/11503492/219105
  """
  years = [(ta[0] - transactions[0][0]).days / 365.0 for ta in transactions]
  residual = 1
  step = 0.05
  guess = 0.05
  epsilon = 0.0001
  limit = 10000
  while abs(residual) > epsilon and limit > 0:
    limit -= 1
    residual = 0.0
    for i, ta in enumerate(transactions):
      residual += ta[1] / pow(guess, years[i])
    if abs(residual) > epsilon:
      if residual > 0:
        guess += step
      else:
        guess -= step
        step /= 2.0
  return guess-1

def shrink_nav_data(nav_data, rank_data):
  """
  Shrinks nav_data array to the size of rank_data array
  by removing rows until the date of the first row in nav_data
  array matches that of rank_data array.
  """
  print 'Shrinking nav_data ...',
  # print '\toriginal size - %d' % len(nav_data)
  target_date = rank_data[1].split(',')[0]
  i = 0
  cnt = len(nav_data)
  for i in range(0, cnt):
    curr_date = nav_data[i].split(',')[0]
    if curr_date == target_date:
      break
  del nav_data[1:i]
  print 'done'
  # print '\tmodified size - %d' % len(nav_data)

def init_units_dict(fund_names):
  """
  Returns a dictionary using the given list of fund names.
  The key is the fund name, the value is set to 0 (units).
  """
  units_dict = {}
  for f in fund_names:
    units_dict[f] = 0
  return units_dict

def get_nav_dict(fund_names, nav_line):
  """
  Returns a dictionary using the given parameters.
  The key is the fund name, the value is the nav.
  """
  nav_dict = {}
  cnt = len(nav_line)
  for i in range(0, cnt):
    fund = fund_names[i]
    nav = nav_line[i]
    nav_dict[fund] = nav
  return nav_dict
  
def get_wealth(nav_dict, units_dict):
  """
  Calculates the portfolio value by multiplying units invested in each fund
  with its corresponding nav.
  """
  wealth = 0.0
  for fund in units_dict:
    wealth += float(nav_dict[fund]) * float(units_dict[fund])
  return wealth

def stats(nav_data, rank_data):
  """
  Generates returns statistics using the given sharpe ratio ranking data.
  """
  
  # remove redundant entries in nav_data
  shrink_nav_data(nav_data, rank_data)

  # retrieve fund names
  fund_names = nav_data[0].split(',')[1:]

  # initialize units dictionary
  units_dict_halfyr = init_units_dict(fund_names)
  units_dict_annual = init_units_dict(fund_names)
  units_dict_overall = init_units_dict(fund_names)
    
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
      nav_dict = get_nav_dict(fund_names, nav_line)
      wealth = get_wealth(nav_dict, units_dict_halfyr)
      cf = (dt, wealth)
      cashflows_halfyr.append(cf)
      ret = xirr(cashflows_halfyr) * 100.0
      returns_halfyr.append(ret)
      del cashflows_halfyr[:]
      for f in units_dict_halfyr:
        units_dict_halfyr[f] = 0
      
    # compute returns every year
    if i % 12 == 0 and i > 0:
      nav_line = nav_data[i].split(',')[1:]
      nav_dict = get_nav_dict(fund_names, nav_line)
      wealth = get_wealth(nav_dict, units_dict_annual)
      cf = (dt, wealth)
      cashflows_annual.append(cf)
      ret = xirr(cashflows_annual) * 100.0
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
  nav_dict = get_nav_dict(fund_names, nav_line)
  wealth = get_wealth(nav_dict, units_dict_overall)
  
  # absolute return
  abs_return = ((wealth / total_inv) - 1) * 100.0
  
  # annualized return
  last_date = nav_data[cnt - 1].split(',')[0]
  dt = datetime.strptime(last_date, '%d-%m-%Y')
  cf = (dt, wealth)
  cashflows_overall.append(cf)
  annual_return = xirr(cashflows_overall) * 100.0

  print '\n'
  print 'Final Investment'
  print '----------------'
  for f in units_dict_overall:
    if units_dict_overall[f] > 0:
      print f, units_dict_overall[f]
  
  print '\n'
  print 'Performance Measures'
  print '--------------------'
  print 'Investment - %s' % "{:,}".format(total_inv)  
  print 'Wealth - %s' % "{:,}".format(int(round(wealth)))
  print 'Absolute return - %s%%' % round(abs_return, 2)
  print 'Annual return - %s%%' % round(annual_return, 2)
  print '\n'

  rf_rate_halfyr = 4.5
  rf_rate_annual = 9.0
  
  print 'Half-Yearly Returns'
  print '-------------------'
  print ''
  for r in returns_halfyr:
    print '%s%%' % round(r, 2)
  print ''
  print 'Number of data points - %d' % len(returns_halfyr)
  print 'Average - %s%%' % round(numpy.mean(returns_halfyr), 2)
  print 'Standard Deviation - %s%%' % round(numpy.std(returns_halfyr), 2)
  print 'Sharpe Ratio - %r' % round(sharpeRanking.get_sharpe_ratio(returns_halfyr, rf_rate_halfyr), 2)
  print '\n'

  print 'Annual Returns'
  print '--------------'
  print ''
  for r in returns_annual:
    print '%s%%' % round(r, 2)
  print ''
  print 'Number of data points - %d' % len(returns_annual)
  print 'Average - %s%%' % round(numpy.mean(returns_annual), 2)
  print 'Standard Deviation - %s%%' % round(numpy.std(returns_annual), 2)
  print 'Sharpe Ratio - %r' % round(sharpeRanking.get_sharpe_ratio(returns_annual, rf_rate_annual), 2)
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