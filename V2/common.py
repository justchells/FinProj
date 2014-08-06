#!/usr/bin/python

import os
import numpy
from collections import defaultdict

data_dir = 'data'
nav_file = 'diversified_2001.csv'
# nav_file = 'largeCap_2001.csv'
sharpe_data_file = 'sharpeData.csv'

mnt_inv = 1000
default_rf_rate = 9.0 / 100.0

nav_data = None
sharpe_data = None

def header(name):

  print '\n'
  print '-' * 50
  print name
  print '-' * 50
  print ''

def get_nav_data():
  
  if nav_data: return nav_data
  set_nav_data()
  return nav_data

def set_nav_data():
  
  global nav_data
  nav_file_path = os.path.join(data_dir, nav_file)
  nav_data = read_from_file(nav_file_path)

def get_sharpe_data():
  
  if sharpe_data: return sharpe_data
  set_sharpe_data()
  return sharpe_data

def set_sharpe_data():
  
  global sharpe_data
  sharpe_data = []
  header = nav_data[0]
  sharpe_data.append(header)
  num_cols = len(header.split(','))
  nav_dict = defaultdict(list)
  
  num_rows = len(nav_data)
  for i, r in enumerate(nav_data):
  
    if i == 0 or i == (num_rows - 1): continue
    
    nav_line = r.split(',')
    dt = nav_line[0]
    for j in xrange(1, num_cols):
      nav_dict[j].append(float(nav_line[j])) 

    if len(nav_dict[1]) == 13:
      row = [dt]
      for j in xrange(1, num_cols):
        n = nav_dict[j]
        ret = [ ((n[k] / n[k-1]) - 1) for k in xrange(1, 13) ]
        sharpe = get_sharpe(ret, 'monthly')
        row.append(str(sharpe))
        n.pop(0) 
    
      line_data = ','.join(row)
      sharpe_data.append(line_data)
 
  sharpe_data_file_path = os.path.join(data_dir, sharpe_data_file)
  write_to_file(sharpe_data_file_path, sharpe_data)
  
def get_fund_nav_dict(fund_names, nav_line):

  fund_nav_dict = {}
  for fund, nav in zip(fund_names, nav_line):
    fund_nav_dict[fund] = float(nav)
  return fund_nav_dict
  
def read_from_file(input_file):
  """
  Returns the file contents in a list.
  The EOL character \n is stripped from each line.
  """

  msg = 'reading from %s ...' % (input_file)
  print msg,
  file_data = []
  with open(input_file, 'r') as f:
    for line in f:
      file_data.append(line.rstrip())
  print 'done'
  print 'no. of lines read: %d' % len(file_data)
  return file_data

def append_to_file(out_file, file_data):
  write_to_file(out_file, file_data, 'a')
  
def write_to_file(out_file, file_data, write_mode = 'w'):
  """
  Write the file data to the output file.
  """
  mode = 'Writing' if write_mode == 'w' else 'Appending'
  msg = '%s to %s ...' % (mode, out_file)
  print msg,
  with open(out_file, write_mode) as f:
    for d in file_data:
      line = str(d) + '\n'
      f.write(line)
  print 'done'
  print 'no. of lines written: %d' % len(file_data)

def get_rf_rate(freq):
  if freq == 'monthly': return default_rf_rate / 12.0
  return default_rf_rate
  
def get_sharpe(ret_data, freq):
  rf_rate = get_rf_rate(freq)
  mean = numpy.mean(ret_data)
  stdev = numpy.std(ret_data)
  mnt_sharpe = (mean - rf_rate) / stdev
  return mnt_sharpe
  
def xirr(transactions):
  """
  Code taken from stackoverflow.com - 
  http://stackoverflow.com/a/11503492/219105
  """
  try:
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
  except:
    print 'encountered error when computing xirr, returning 0'
    return 0