#!/usr/bin/python

import os

def create_dir(dir_path):
  """
  Create the directory (and its parents) if it doesn't exist.
  """
  if not os.path.exists(dir_path):
    print 'creating directory - %s' % dir_path
    os.makedirs(dir_path)
  pass

def init_dict(fund_names):
  """
  Returns a dictionary using the given list of fund names.
  The key is the fund name, the value is set to 0 (units).
  """
  dict = {}
  for f in fund_names:
    dict[f] = 0
  return dict

def init_array_dict(fund_names):
  """
  Returns a dictionary using the given list of fund names.
  The key is the fund name, the value is set to 0 (units).
  """
  dict = {}
  for f in fund_names:
    dict[f] = []
  return dict


def get_fund_nav_dict(fund_names, nav_line):
  """
  Returns a dictionary using the given parameters.
  The key is the fund name, the value is the nav.
  """
  fund_nav_dict = {}
  cnt = len(nav_line)
  for i in range(0, cnt):
    fund = fund_names[i]
    nav = nav_line[i]
    fund_nav_dict[fund] = nav
  return fund_nav_dict
  
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

