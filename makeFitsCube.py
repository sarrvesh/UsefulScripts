#!/usr/bin/env python
"""
makeFitsCube.py

This script is intended for merging channel maps into a FITS cube.

Written by Sarrvesh S. Sridhar

To do list:
* Change all pyFits dependencies to AstroPy
"""
import optparse
try: import psutil
except IOError: raise Exception('Unable to import psutil.')
try: import pyfits as pf
except IOError: raise Exception('Unable to import pyFits.')

version_string = 'v1.0, 8 June 2015\nWritten by Sarrvesh S. Sridhar'
print 'makeFitsCube.py', version_string 
print ''

def main(options):
    # First do some system diagnostics
    availPhysMem = psutil.virtual_memory().total
    print 'INFO: Detected {} MB of physical memory'.format(availPhysMem/(1024*1024))
    availSwapMem = psutil.swap_memory().total
    print 'INFO: Detected {} MB of swap memory'.format(availSwapMem/(1024*1024))
    
    # Estimate the code's memory requirements
    

if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option('-i', '--in', help='Glob selection string for input files '+\
                    '[no default]', default='')
    opt.add_option('-o', '--out', help='Filename of the output cube '+\
                   '[default: mergedFits.fits]', default='mergedFits.fits')
    opt.add_option('-m', '--mmap', help='Use memory map to store temporary '+\
                   'arrays instead of physical memory [default=False]', default=False, \
                   action='store_true')
    options, arguments = opt.parse_args()
    main(options)
