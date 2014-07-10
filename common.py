#!/usr/bin/python

import os
import numpy

rf_rate = 9.00 / 100.0

def get_rf_rate(freq):
  """
  Returns the risk-free rate for the given frequency.
  Following frequency values are supported:
    - monthly
    - quarterly
    - half-yearly
    - annual
  If an unsupported value is used, the annual risk-free rate is returned.
  """
  if freq == 'monthly':
    return rf_rate / 12.0
  elif freq == 'quarterly':
    return rf_rate / 4.0
  elif freq == 'half-yearly':
    return rf_rate / 2.0
  else:
    return rf_rate
  
def get_sharpe_ratio(return_data, rf_rate):
  """
  Returns the sharpe ratio for the given returns and risk-free rate.
  """
  
  mean = numpy.mean(return_data)
  stdev = numpy.std(return_data)
  sharpe_ratio = (mean - rf_rate) / stdev
  return sharpe_ratio

def create_dir(dir_path):
  """
  Create the directory (and its parents) if it doesn't exist.
  """
  if not os.path.exists(dir_path):
    print 'creating directory - %s' % dir_path
    os.makedirs(dir_path)
  pass

def init_dict(keys):
  """
  Returns a dictionary using the given keys.
  The value for each key is set to 0.
  """
  dict = {}
  for k in keys:
    dict[k] = 0
  return dict

def init_array_dict(keys):
  """
  Returns a dictionary using the given keys.
  The value for each key is set to an empty array.
  """
  dict = {}
  for k in keys:
    dict[k] = []
  return dict


def get_fund_nav_dict(fund_names, fund_nav):
  """
  Returns a dictionary using the given parameters.
  The key is the fund name, the value is the nav.
  """
  fund_nav_dict = {}
  cnt = len(fund_nav)
  for i in range(0, cnt):
    fund = fund_names[i]
    nav = fund_nav[i]
    fund_nav_dict[fund] = nav
  return fund_nav_dict

def get_fund_wealth(nav_dict, units_dict):
  wealth = {}
  for fund in units_dict:
    wealth[fund] = float(nav_dict[fund]) * float(units_dict[fund])
  return wealth

  
def trim_data(nav_data, target_date):
  """
  Removes entries in the nav_data array from the top
  until a row with the given date is found.
  """
  print 'Trimming nav_data ...',
  i = 0
  oldLen = len(nav_data)
  for i in range(0, oldLen):
    curr_date = nav_data[i].split(',')[0]
    if curr_date == target_date:
      break
  del nav_data[1:i]
  print 'done'
  newLen = len(nav_data)
  print 'old size - %d, new size - %d' % (oldLen, newLen)

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

def write_to_file(output_file, file_data):
  """
  Write the file data to the output file.
  """
  msg = 'Writing to %s ...' % (output_file)
  print msg,
  with open(output_file, 'w') as f:
    for d in file_data:
      line = str(d) + '\n'
      f.write(line)
  print 'done'
  print 'no. of lines written: %d' % len(file_data)

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
