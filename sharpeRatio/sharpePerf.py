import financial
import sys
import sharpeRanking
from datetime import datetime

monthly_inv = 1000
precision = 4

def portfolio_value(rank_data, nav_data):
  units_dict = {}
  latest_nav_dict = {}
  cashflows = []
  num_rows = len(rank_data)
  
  # calculate investment amount
  # header row and last row is skipped
  num_inv = num_rows - 2 
  inv_amt = num_inv * monthly_inv

  # compute units invested in top ranked funds for each month
  # also initialize the cashflows list (used for computing xirr)
  # header row and last row is skipped
  start = 1
  end = num_rows - 1
  for i in range(start, end):
    (date, fund, nav) = rank_data[i].split(',')
    units = monthly_inv / float(nav)
    if fund in units_dict:
      units_dict[fund] += units
    else:
      units_dict[fund] = units
    dt = datetime.strptime(date, '%d-%m-%Y')
    cf = (dt, -monthly_inv)
    cashflows.append(cf)
  
  # store latest nav for each fun
  nav_cnt = len(nav_data)
  nav_header = nav_data[0].split(',')
  num_cols = len(nav_header)
  nav_line = nav_data[nav_cnt - 1].split(',')
  for i in range(1, num_cols):
    fund = nav_header[i]
    nav = nav_line[i]
    latest_nav_dict[fund] = float(nav)
  
  # calculate portfolio value
  wealth = 0
  print '\nInvestment Details (Fund, Units)'
  print '--------------------------------'
  for k in sorted(units_dict.keys()):
    print k, round(units_dict[k], 2)
    wealth += latest_nav_dict[k] * units_dict[k]
  
  # update cashflows list with final value
  last_date = nav_line[0]
  dt = datetime.strptime(last_date, '%d-%m-%Y')
  cf = (dt, wealth)
  cashflows.append(cf)
  
  # calculate return
  abs_return = ((wealth / inv_amt) - 1) * 100.0

  # calculate xirr
  annual_return = financial.xirr(cashflows) * 100.0
  
  # display stats
  print '\nInvestment amount - %s' % "{:,}".format(inv_amt)  
  print 'Portfolio value - %s' % "{:,}".format(int(round(wealth)))
  print 'Absolute return - %s%%' % round(abs_return, 2)
  print 'Annual return - %s%%' % round(annual_return,2)
  
def avg_halfyr_xirr():
  pass
  
def avg_annual_xirr():
  pass
  
def overall_sharpe_halfyr():
  pass
  
def overall_sharpe_annual():
  pass
  
def run(rank_file, nav_file):
  rank_data = sharpeRanking.read_from_file(rank_file)
  print 'No. of lines read: %d' % len(rank_data)
  nav_data = sharpeRanking.read_from_file(nav_file)
  print 'No. of lines read: %d' % len(nav_data)
  portfolio_value(rank_data, nav_data)
  
def main():
  """
  Main function. Defined for command line. Calls run().
  """
  script, sharpe_rank_file, nav_file = sys.argv
  run(sharpe_rank_file, nav_file)
  
if __name__ == '__main__':
  main()