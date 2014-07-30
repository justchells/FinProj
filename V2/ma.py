#!/usr/bin/python

import os
import common
from collections import defaultdict
from datetime import datetime

out_dir = 'output'
out_file = 'flexStp.csv'

type = None
period = None
num_rows = None
nav_data = None
fund_names = None

inc_factor = 0.25
max_factor = 2.0

def set_global_vars(t, p):
  
  global type, period, nav_data, num_rows, fund_names
  type = t
  period = p
  nav_data = common.get_nav_data()
  num_rows = len(nav_data)
  fund_names = nav_data[0].split(',')[1:]
  
def compute_returns():

  default_inv = common.mnt_inv
  min_inv = 0
  max_inv = default_inv * max_factor
  increment = default_inv * inc_factor
  
  for i,r in enumerate(nav_data):
    
    if i < 13 or i == (num_rows - 1): continue
  
  pass
  
def compute_risk():
  pass
  
def save():
  pass
  
def run(type, period):
  
  set_global_vars(type, period)
  compute_returns()
  compute_risk()
  save()