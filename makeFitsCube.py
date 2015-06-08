#!/usr/bin/env python
"""
makeFitsCube.py

This script is intended for merging channel maps into a FITS cube.

Written by Sarrvesh S. Sridhar

To do list:
* Change all pyFits dependencies to AstroPy
"""
import optparse
import glob
import os
try: import numpy as np
except ImportError: raise Exception('Unable to import Numpy')
try: import psutil
except ImportError: raise Exception('Unable to import psutil.')
try: import pyfits as pf
except ImportError: raise Exception('Unable to import pyFits.')

version_string = 'v1.0, 8 June 2015\nWritten by Sarrvesh S. Sridhar'
print 'makeFitsCube.py', version_string 
print ''

def getValidFitsList(fileList):
    validFitsList = []
    for name in fileList:
        if 'FITS' in os.popen('file {}'.format(name)).read():
            validFitsList.append(name)
    return validFitsList

def checkFitsShape(fitsList):
    for i, name in enumerate(fitsList):
        if i == 0:
            templateShape = pf.open(name, readonly=True)[0].data[0].shape
        elif templateShape == pf.open(name, readonly=True)[0].data[0].shape: pass
        else:
            raise Exception('Fits file {} has an incompatible shape'.format(name))
    return templateShape

def main(options):
    # Check user input
    if options.inp == '':
        raise Exception('An input glob string must be specified.')
    if options.out == '':
        raise Exception('An output filename must be specified.')
    
    # First do some system diagnostics
    availPhysMem = psutil.virtual_memory().total
    print 'INFO: Detected {} MB of physical memory'.format(availPhysMem/(1024*1024))
    availSwapMem = psutil.swap_memory().total
    print 'INFO: Detected {} MB of swap memory'.format(availSwapMem/(1024*1024))
    
    # Get the list of FITS files
    fileList = sorted(glob.glob(options.inp))
    validFitsList = getValidFitsList(fileList)
    print 'INFO: Identified {} fits files from {} files selected by input string'.\
          format(len(validFitsList), len(fileList))
    
    # Check if the list of supplied fits files have the same shape
    shape = checkFitsShape(validFitsList)
    print 'All fits files have shape {}'.format(shape)
    # Estimate the size requirements for the selected list of fits files
    #totPixels = 0
    #for name in validFitsList:
        #totPixels += getNumOfPixels(name)
        #getNumOfPixels(name)
    

if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option('-i', '--inp', help='Glob selection string for input files '+\
                    '[no default]', default='')
    opt.add_option('-o', '--out', help='Filename of the output cube '+\
                   '[default: mergedFits.fits]', default='mergedFits.fits')
    opt.add_option('-m', '--mmap', help='Use memory map to store temporary '+\
                   'arrays instead of physical memory [default=False]', default=False, \
                   action='store_true')
    opt.add_option('-f', '--freq', help='Write the list of frequencies to a text file', \
                   default=False, action='store_true')
    options, arguments = opt.parse_args()
    main(options)
