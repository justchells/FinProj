#!/usr/bin/python

import os
import common
from collections import defaultdict
from datetime import datetime

output_dir = 'output'
output_file = 'flexStp.csv'

mnt_inv = None
num_rows = None
nav_data = None
fund_names = None

perf_dict = defaultdict()
risk_dict = defaultdict(float)

def set_global_vars():
  global nav_data, fund_names, num_rows, mnt_inv
  nav_data = common.get_nav_data()
  fund_names = nav_data[0].split(',')[1:]
  num_rows = len(nav_data)
  mnt_inv = common.mnt_inv

def compute_returns():
  pass

def compute_risk():
  pass

def save():
  pass
  
def run():
  set_global_vars()
  compute_returns()
  compute_risk()
  save()