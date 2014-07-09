#!/usr/bin/python

import os
import sys
import numpy
import common

data_dir = 'data'
sharpe_data_file_name = 'sharpeData.csv'
sharpe_rank_file_name = 'sharpeRank.csv'

def get_return_data(nav_data):
  """
  Returns a list with the monthly returns for each fund.
  """
  
  returns = []
  cnt = len(nav_data)
  for i in range(1, cnt):
    p = float(nav_data[i - 1])
    n = float(nav_data[i])
    r = (n / p) - 1.0
    returns.append(r)
  return returns

def get_sharpe_ratio(return_data, rf_rate):
  """
  Returns the sharpe ratio for the given returns and risk-free rate.
  """
  
  mean = numpy.mean(return_data)
  stdev = numpy.std(return_data)
  sharpe_ratio = (mean - rf_rate) / stdev
  return sharpe_ratio
  
def get_sharpe_data(nav_data):
  """
  Returns a list with the monthly sharpe ratio for each fund.
  A rolling window of last 12 months is used to compute the sharpe ratio.
  
  Input Format
  ------------
  Date, NAV1, NAV2, NAV3, ...
  
  Output Format
  -------------
  Date, Sharpe1, Sharpe2, Sharpe3, ...
  """

  sharpe_data = []
  rf_rate = common.get_rf_rate('monthly')
  print rf_rate
  
  # save header row
  header = nav_data[0]
  sharpe_data.append(header)
  
  # initialize dictionary that will hold nav for last 12 months for each fund
  nav_dict = {}
  num_cols = len(header.split(','))
  for i in range(1, num_cols):
    nav_dict[i] = []

  # monthly sharpe ratio
  # header row is skipped
  cnt = len(nav_data)
  for i in range(1, cnt):
    
    nav_line = nav_data[i].split(',')
    
    # add nav to respective list in nav dictionary
    for j in range(1, num_cols):
      nav_dict[j].append(nav_line[j]) 

    # rolling window of last 12 months
    if len(nav_dict[1]) > 12:
      row = []
      
      # date column
      row.append(str(nav_line[0])) 
      
      # compute sharpe ratio for each fund
      for j in range(1, num_cols):
        return_data = get_return_data(nav_dict[j])
        sharpe_ratio = get_sharpe_ratio(return_data, rf_rate)
        row.append(str(sharpe_ratio))
        
        # remove the first element to move the window
        nav_dict[j].pop(0) 
    
      line_data = ','.join(row)
      sharpe_data.append(line_data)

  return sharpe_data
  
def get_sharpe_rank_data(nav_data, sharpe_data):
  """
  Returns a list with the highest ranked fund for each month.
  The ranking is based on the monthly sharpe ratio. 
  
  Input Format
  ------------
  nav_data -> Date, NAV1, NAV2, NAV3, ...
  sharpe_data -> Date, Sharpe1, Sharpe2, Sharpe3, ...
  
  Output Format
  -------------
  Date, Fund, NAV
  """
  
  sharpe_rank_data = []
  
  header_line = 'Date,Fund,NAV'
  sharpe_rank_data.append(header_line)
  
  # ensure both arrays are of the same length
  target_date = sharpe_data[1].split(',')[0]
  common.trim_data(nav_data, target_date)
  assert len(nav_data) == len(sharpe_data)
  
  # initialize a dictionary for accessing fund names based on the column index
  # {key, value} = {columnIndex, fundName}
  col_fund_dict = {}
  header_row = nav_data[0].split(',')
  num_cols = len(header_row)
  for i in range(0, num_cols):
    col_fund_dict[i] = header_row[i]

  # rank funds based on sharpe ratio
  # header row is skipped
  num_rows = len(sharpe_data)
  for i in range(1, num_rows):
    row_data = sharpe_data[i].split(',')
    
    # identify the fund with the highest sharpe ratio for the month
    max_ind = 1
    max_val = row_data[1]
    for j in range(1, num_cols):
      if float(row_data[j]) > float(row_data[max_ind]):
        max_ind = j
        max_val = row_data[j]
    
    date = row_data[0]
    fund = col_fund_dict[max_ind]
    nav = nav_data[i].split(',')[max_ind]
    line_data = date + "," + fund + "," + nav
    sharpe_rank_data.append(line_data)
    
  return sharpe_rank_data

def run(nav_file):
  """
  Generates monthly sharpe ratio for each fund using a rolling window of the 
  last 12 months. Uses this data to generate a rank file that specifies which 
  fund to invest in each month. The fund chosen each month is the one with the 
  highest sharpe ratio.
  """
  
  # create data directory
  common.create_dir(data_dir)
  
  # read nav data
  nav_data = common.read_from_file(nav_file)
  
  # generate monthly sharpe ratio
  sharpe_data = get_sharpe_data(nav_data)
  sharpe_data_file = os.path.join(data_dir, sharpe_data_file_name)
  common.write_to_file(sharpe_data_file, sharpe_data)

  # generate sharpe ranking
  sharpe_rank_data = get_sharpe_rank_data(nav_data, sharpe_data)
  sharpe_rank_data_file = os.path.join(data_dir, sharpe_rank_file_name)
  common.write_to_file(sharpe_rank_data_file, sharpe_rank_data)

  
def main():
  script, nav_file = sys.argv
  run(nav_file)
  
  
if __name__ == '__main__':
  main()

