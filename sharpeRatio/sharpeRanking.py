#!/usr/bin/python
# Copyright 2014 Karthikeyan Chellappa

# LOGIC
# generate the sharpe ratio for each month based on returns of last 12 months
# create an output file containing sharpe ratio for each month under each fund (date, fund1, fund2, etc.)
# using this file, compute the rank for each month based on the highest sharpe ratio
# create an output file with the highest ranked fund for each month, including its NAV (date, fund, nav)

# CONDITIONS
# No changes required if an additional column is added
# No changes required if additional rows are added

import sys
import numpy

rfRate = 0.0075 # 9% / 12
precision = 4

def get_return_data(nav):
  """
  Returns a list with the returns for each month for the given nav.
  
  Expected format for nav -> [nav]
  Output format -> [return]
  """
  returns = []
  cnt = len(nav)
  for i in range(1, cnt):
    p = float(nav[i - 1])
    n = float(nav[i])
    r = round((n / p) - 1.0, precision)
    returns.append(r)
  return returns

def get_sharpe_ratio(return_data, rf_rate):
  """
  Returns the sharpe ratio for the given nav.
  
  Expected format for nav -> [nav]
  """
  mean = numpy.mean(return_data)
  stdev = numpy.std(return_data)
  sharpe_ratio = round((mean - rf_rate) / stdev, precision)
  return sharpe_ratio
  
def get_sharpe_data(nav_data):
  """
  Returns a list with the sharpe ratio for each month under each fund.
  
  Expected format for nav_data -> [date, nav1, nav2, ...]
  Output format -> [date, sharpe1, sharpe2, ...]
  """
  sharpe_data = []

  # save header row
  header = nav_data[0]
  sharpe_data.append(header)
  
  # initialize the column dictionary
  colDict = {}
  colNum = len(header.split(','))
  for i in range(1, colNum):
    colDict[i] = []
  
  # loop through the rows
  cnt = len(nav_data)
  for i in range(1, cnt):
    line = nav_data[i]
    cols = line.split(',')
    
    # add nav to respective list in dictionary
    for j in range(1, colNum):
      colDict[j].append(cols[j]) 

    # rolling window of last 12 months
    if len(colDict[1]) > 12:
      line = []
      line.append(str(cols[0]))
      
      # compute the sharpe ratio for each fund
      for j in range(1, colNum):
        return_data = get_return_data(colDict[j])
        sharpe_ratio = get_sharpe_ratio(return_data, rfRate)
        line.append(str(sharpe_ratio))
        colDict[j].pop(0) # remove the first element to move the window
    
      data = ','.join(line)
      sharpe_data.append(data)

  return sharpe_data

def trim_nav_data(nav_data, sharpe_data):
  """
  Trims the elements from the head of nav_data list until the date matches the
  first entry in the sharpe_data list.
  """
  target_date = sharpe_data[1].split(',')[0]
  i = 0
  cnt = len(nav_data)
  for i in range(0, cnt):
    dt = nav_data[i].split(',')[0]
    if dt == target_date:
      break
  del nav_data[1:i]
  return nav_data
  
def get_sharpe_rank_data(nav_data, sharpe_data):
  """
  Returns a list with the highest ranked fund for each month based on sharpe 
  ratio. The input parameter, sharpe_data, is a list with all applicable funds 
  and their corresponding sharpe ratio. Input parameters, nav_data and 
  sharpe_data should be of the same length.
  
  Expected format for nav_data -> [date, nav1, nav2, ...]
  Expected format for sharpe_data -> [date, sharpe1, sharpe2, ...]
  Output format -> [date, fund, nav]
  """
  
  sharpe_rank_data = ["Date,Fund,NAV"]
  
  # ensure both arrays are of the same length
  assert len(nav_data) == len(sharpe_data)
  
  # initialize the dictionary
  fundDict = {}
  header = nav_data[0]
  cols = header.split(',')
  colNum = len(cols)
  for i in range(0, colNum):
    fundDict[i] = cols[i]

  # loop through the rows
  rowNum = len(sharpe_data)
  for i in range(1, rowNum):
    line = sharpe_data[i].split(',')
    maxInd = 1
    maxVal = line[1]
    for j in range(1, colNum):
      if float(line[j]) > float(line[maxInd]):
        maxInd = j
        maxVal = line[j]
    data_line = line[0] + "," + fundDict[maxInd] + "," + nav_data[i].split(',')[maxInd]
    sharpe_rank_data.append(data_line)
    
  return sharpe_rank_data

def read_from_file(input_file):
  """
  Returns the file contents in a list.
  The EOL character \n is stripped from each line.
  """
  msg = 'Reading from %s ...' % (input_file)
  print msg,
  file_data = []
  with open(input_file, 'r') as f:
    for line in f:
      file_data.append(line.rstrip())
  print 'done'
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

def run(nav_file):
  """
  Executes the logic as defined for this module.
  """
  nav_data = read_from_file(nav_file)
  print 'number of lines read: %d' % len(nav_data)
  
  sharpe_data = get_sharpe_data(nav_data)
  write_to_file('sharpeData.csv', sharpe_data)

  nav_data_trimmed = trim_nav_data(nav_data, sharpe_data)
  sharpe_rank_data = get_sharpe_rank_data(nav_data_trimmed, sharpe_data)
  write_to_file('sharpeRankData.csv', sharpe_rank_data)
  
def main():
  """
  Main function. Used for command line. Call run().
  """
  script, nav_file = sys.argv
  run(nav_file)
  
if __name__ == '__main__':
  main()
