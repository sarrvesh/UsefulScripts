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
try:
    import numpy as np
except ImportError:
    raise Exception('Unable to import Numpy')
try:
    import psutil
except ImportError:
    raise Exception('Unable to import psutil.')
try:
    import pyfits as pf
except ImportError:
    raise Exception('Unable to import pyFits.')

version_string = 'v1.0, 8 June 2015\nWritten by Sarrvesh S. Sridhar'
print 'makeFitsCube.py', version_string
print ''

def getValidFitsList(fileList):
    """
    Extracts fits files from a list of files using its magic number.
    """
    validFitsList = []
    for name in fileList:
        if 'FITS' in os.popen('file {}'.format(name)).read():
            validFitsList.append(name)
    return validFitsList

def checkFitsShape(fitsList):
    """
    Checks if the list of fits files all have the same shape.
    If True, return the shape and memory in bytes of a single fits file
    If False, raises an exception causing the execution to terminate
    """
    for i, name in enumerate(fitsList):
        if i == 0:
            templateShape = pf.open(name, readonly=True)[0].data[0].shape
            templateSize = pf.open(name, readonly=True)[0].data[0].nbytes
        elif templateShape == pf.open(name, readonly=True)[0].data[0].shape:
            pass
        else:
            raise Exception('Fits file {} has an incompatible shape'.format(name))
    return templateShape, templateSize

def concatenateWithRAM(validFitsList, shape):
    """
    Concatenate a given list of fits files into a single cube
    """
    concatCube = np.zeros((1, len(validFitsList), shape[-2], shape[-1]))
    print concatCube.shape

def main(options):
    """
    Main function
    """
    # Check user input
    if options.inp == '':
        raise Exception('An input glob string must be specified.')
    if options.out == '':
        raise Exception('An output filename must be specified.')
    # Get the list of FITS files
    fileList = sorted(glob.glob(options.inp))
    validFitsList = getValidFitsList(fileList)
    print 'INFO: Identified {} fits files from {} files selected by input string'.\
          format(len(validFitsList), len(fileList))
    # Proceed with the execution if we have non-zero FITS files
    if len(validFitsList) == 0:
        raise Exception('No valid fits files were selected by the glob string')
    # Check if the list of supplied fits files have the same shape
    shape, fitsSize = checkFitsShape(validFitsList)
    print 'INFO: All fits files have shape {}'.format(shape)
    if len(shape) not in [2, 3, 4]:
        raise Exception('Fits files have unknown shape')
    totalArraySize = fitsSize*len(validFitsList)/(1024*1024)
    print 'INFO: Total required memory is {} MB'.format(totalArraySize)
    availMem = psutil.virtual_memory().available/(1024*1024)
    print 'INFO: Available physical memory is {} MB'.format(availMem)

    # Decide whether to use RAM or memory map to store the temporary files
    if totalArraySize > availMem:
        print 'INFO: Memory required by the code is greater than available memory.'
        print 'INFO: Will use memory map to store temporary files.'
    else:
        print 'INFO: Using physical memory to store temporary files.'
        concatenateWithRAM(validFitsList, shape)

if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option('-i', '--inp', help='Glob selection string for input files '+\
                    '[no default]', default='')
    opt.add_option('-o', '--out', help='Filename of the output cube '+\
                   '[default: mergedFits.fits]', default='mergedFits.fits')
    opt.add_option('-f', '--freq', help='Write the list of frequencies to a text file', \
                   default=False, action='store_true')
    inOpts, arguments = opt.parse_args()
    main(inOpts)
