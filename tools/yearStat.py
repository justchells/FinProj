#!/usr/bin/python

from collections import defaultdict

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
  
def main():
  nav_data = read_from_file('diversified.csv')
  del nav_data[0]
  
  yearStats = []
  
  for i,r in enumerate(nav_data):
    if i % 12 != 0: continue
    dt = r.split(',')[0]
    
    nav_line = r.split(',')[1:]
    
    cnt = 0
    for n in nav_line:
      if n: cnt += 1
    
    stat = (dt, cnt)
    yearStats.append(stat)
  
  for s in yearStats:
    print s
  
if __name__ == '__main__':
  main()