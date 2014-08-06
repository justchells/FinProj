#!/usr/bin/python

import common

num_rows = None
nav_data = None
fund_names = None

def set_global_vars():
  
  global nav_data, fund_names, num_rows
  nav_data = common.get_nav_data()
  fund_names = nav_data[0].split(',')[1:]
  num_rows = len(nav_data)

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