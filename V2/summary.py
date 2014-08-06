#!/usr/bin/python

import os
import numpy
import common

sort_order_dict = {
  'Regular SIP': 1,
  'Flex STP': 2,
  'MA Normal 3 months': 3,
  'MA Normal 6 months': 4,
  'MA Normal 9 months': 5,
  'MA Normal 12 months': 6,
  'MA Inverted 3 months': 7,
  'MA Inverted 6 months': 8,
  'MA Inverted 9 months': 9,
  'MA Inverted 12 months': 10,
}

out_file_dict = {
  'Regular SIP': 'regularSip.csv',
  'Flex STP': 'flexStp.csv',
  'MA Normal 3 months': 'ma_normal_3_month.csv',
  'MA Normal 6 months': 'ma_normal_6_month.csv',
  'MA Normal 9 months': 'ma_normal_9_month.csv',
  'MA Normal 12 months': 'ma_normal_12_month.csv',
  'MA Inverted 3 months': 'ma_inverted_3_month.csv',
  'MA Inverted 6 months': 'ma_inverted_6_month.csv',
  'MA Inverted 9 months': 'ma_inverted_9_month.csv',
  'MA Inverted 12 months': 'ma_inverted_12_month.csv',
}

def sort_val(key):

  return sort_order_dict[key]

def run():
  
  file_data = []
  header_line = 'Category,Inv Period,Return,Std Dev,Sharpe'
  file_data.append(header_line)

  for header in sorted(out_file_dict, key=sort_val):
    
    out_file = out_file_dict[header]
    out_file_path = os.path.join('output', out_file)
    out_data = common.read_from_file(out_file_path)
    del out_data[0]
    
    inv_period_data = []
    ret_data = []
    sharpe_data = []
    
    for r in out_data:
      
      row_data = r.split(',')
      inv_period_data.append(float(row_data[2]))
      ret_data.append(float(row_data[5]))
      sharpe_data.append(float(row_data[6]))
    
    inv_period = numpy.mean(inv_period_data)
    ret = numpy.mean(ret_data)
    stdev = numpy.std(ret_data)
    sharpe = numpy.mean(sharpe_data)
    
    line_data = header + ',' + str(inv_period) + ',' + str(ret) + ',' \
      + str(stdev) + ',' + str(sharpe)
    file_data.append(line_data)

  rank_file = os.path.join('output', 'ranked.csv')
  rank_data = common.read_from_file(rank_file)
  del rank_data[0]
  
  for r in rank_data:
  
    row_data = r.split(',')
    category = row_data[0].capitalize() + ' ' + row_data[1]
    ret = row_data[5]
    sharpe = row_data[6]
    
    line_data = category + ',1.0,' + ret + ',,' + sharpe
    file_data.append(line_data)
    
  equalWt_file = os.path.join('output', 'equalWt.csv')
  equalWt_data = common.read_from_file(equalWt_file)
  del equalWt_data[0]
  row_data = equalWt_data[0].split(',')
  
  line_data = 'Equal Weighted,1.0,' + row_data[3] + ',,' + row_data[4]
  file_data.append(line_data)
    
  summary_file = os.path.join('output', 'summary.csv')
  common.write_to_file(summary_file, file_data)