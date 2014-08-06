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
  nav_data = read_from_file('largeCap.csv')
  num_rows = len(nav_data)
  fund_names = nav_data[0].split(',')[1:]
  
  gap_data = []
  
  fund_nav_dict = defaultdict(float)
  for i,f in enumerate(fund_names):
    # print 'Validating %s ...' % f
    for j,r in enumerate(nav_data):
      if j == 0: continue
      nav_tracked = fund_nav_dict[f] != 0.0  
      dt = r.split(',')[0]
      fnav = r.split(',')[i + 1]
      if fnav and not nav_tracked:
        # print 'first entry on %s' % dt
        fund_nav_dict[f] = fnav
      if not fnav and nav_tracked:
        # print 'found gap on %s' % dt
        gap = (f, dt)
        gap_data.append(gap)
  
  for g in gap_data:
    print g
        
if __name__ == '__main__':
  main()