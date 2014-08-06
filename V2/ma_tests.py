#!/usr/bin/python

def stats_inc_factor():
  
  global inc_factor
  max_factor = 2.0
  stat_data = []
  
  for v in xrange(0, 101):
    
    val = v / 100.0
    print 'inc_factor - %.2f' % val
    inc_factor = val
    set_global_vars('inverted', 12)
    set_ma_data()
    compute_returns()
    compute_risk()
    
    ret_data = []
    risk_data = []
    for fund in fund_names:
      (investment, wealth, abs_return, ann_return, sharpe) = stats_dict[fund]
      ret_data.append(ann_return)
      risk_data.append(sharpe)
    
    avg_ret = numpy.mean(ret_data)
    avg_risk = numpy.mean(risk_data)
    stat = '%s,%s,%s' % (inc_factor, avg_ret, avg_risk)
    stat_data.append(stat)
  
  out_file_path = os.path.join('output', 'ma_stats_inc_factor.csv')
  common.write_to_file(out_file_path, stat_data)
  
def optimize(target, factor):

  common.header('Optimizing ' + target + ' using ' + factor)

  global inc_factor, max_factor
  inc_factor = 0.25
  max_factor = 2.0
  stat_data = []

  if factor == 'inc_factor':
    min_range = 0
    max_range = 101
    div_factor = 100.0
  elif factor == 'max_factor':
    min_range = 1
    max_range = 11
    div_factor = 2.0
  
  for p in (3, 6, 9, 12):
  
    print '%d months inverted MA' % p
    max_val = 0.0
    opt_val = 0.0
    
    for v in xrange(min_range, max_range):
    
      val = v / div_factor
      if factor == 'inc_factor':
        inc_factor = val
      elif factor == 'max_factor':
        max_factor = val
      
      set_global_vars('inverted', p)
      set_ma_data()
      compute_returns()
      compute_risk()
    
      val_data = []
      for fund in fund_names:
        (investment, wealth, abs_return, ann_return, sharpe) = stats_dict[fund]
        if target == 'returns':
          val_data.append(ann_return)
        elif target == 'risk':
          val_data.append(sharpe)
      curr_val = numpy.mean(val_data)
        
      if curr_val > max_val:
        print 'improved value at %.2f - %.4f' % (val, curr_val)
        opt_val = val
        max_val = curr_val
  
    stat = '%d months MA, %.2f, %.4f' % (p, opt_val, max_val)
    stat_data.append(stat)
  
  print '\nResults'
  print '-' * 10
  print '\n'.join(stat_data)  