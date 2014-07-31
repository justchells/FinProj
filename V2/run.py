#!/usr/bin/python

import sys
import common
import regularSip
import flexStp
import ma
import ranked
import timed

def header(name):
  print '\n'
  print '-' * 50
  print name
  print '-' * 50
  print ''
  
def main():

  header('Loading Data')
  common.set_nav_data()

  header('Regular SIP')
  regularSip.run()
  
  header('Flex STP')
  flexStp.run()
  
  header('Normal MA')
  ma.run('normal', 3)
  ma.run('normal', 6)
  ma.run('normal', 9)
  ma.run('normal', 12)
  
  header('Inverted MA')
  ma.run('inverted', 3)
  ma.run('inverted', 6)
  ma.run('inverted', 9)
  ma.run('inverted', 12)
  
  header('Top Ranked')
  ranked.create_out_file()
  ranked.run('top', 1)
  ranked.run('top', 2)
  ranked.run('top', 3)
  
  header('Bottom Ranked')
  ranked.run('bottom', 1)
  ranked.run('bottom', 2)
  ranked.run('bottom', 3)
  
  header('Timed')
  timed.run()
  
  print '\n'
  
if __name__ == '__main__':
  main()