#!/usr/bin/env python
"""
 plotVisibilityDensity.py

This script plots the visibility density for a given
measurement set.

Written by Sarrvesh S. Sridhar

TODO:
* Provide the option of plotting uvwave instead of uvdist.
"""
import optparse
import numpy as np
import pyrap.tables as pt
import matplotlib.pyplot as plt

def main(options):
   ms = pt.table(options.inms, readonly=True)
   # Read the U and V coodinates
   uCol = ms.getcol('UVW')[:,0]
   vCol = ms.getcol('UVW')[:,1]
   # compute the distance using U and V
   uvdist = np.sqrt(np.add(np.square(uCol), np.square(vCol)))
   # Plot the histogram

if __name__ == '__main__':
   opt = optparse.OptionParser()
   opt.add_option('-i', '--inms', help='Input measurement set '+
                  '[no default]', default='')
#   opt.add_option('-l', '--lambda', help='Plot uvwave instead '+
#                  'of uvdist? [default: False]', default=False, 
#                  action='store_true')
   inOpts, arguments = opt.parse_args()
   if inOpts.inms == '':
      raise Exception('Error: No input MS specified!')
   main(inOpts)
