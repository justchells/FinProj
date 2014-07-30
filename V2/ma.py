#!/usr/bin/python

type = None
period = None

def set_global_vars(t, p):
  
  global type, period
  type = t
  period = p

def compute_returns():
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