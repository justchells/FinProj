#!/usr/bin/python

import os
import numpy

rf_rate = 9.0 / 100.0
mnt_inv = 1000
data_dir = 'data'
nav_file = 'navData.csv'

def get_nav_data():
  nav_file_path = os.path.join(data_dir, nav_file)
  return read_from_file(nav_file_path)

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
  
def get_mnt_sharpe(ret_data):
  rate = rf_rate / 12.0
  mean = numpy.mean(ret_data)
  stdev = numpy.std(ret_data)
  mnt_sharpe = (mean - rate) / stdev
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