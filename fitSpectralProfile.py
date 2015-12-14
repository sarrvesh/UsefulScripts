#!/usr/bin/env python
"""
fitSpectralProfile.py

This script fits a curved spectra to the input images on a pixel-by-pixel
basis.

Written by Sarrvesh S. Sridhar

"""
import optparse
import pyfits as pf

def main(options):
    # Get the input images
    if ',' not in options.input:
        fileNames = options.input
        nFiles = 1
    else:
        fileNames = options.input.split(',')
        nFiles = len(fileNames)
    print 'INFO: No. of input images:', nFiles

if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option('-i', '--input', \
                   help='Comma separated image list [no default]', \
                   default='')
    opt.add_option('-n', '--nterms', \
                   help='No. of spectral terms to fit [default: 1]', \
                   default=1)
    opt.add_option('-p', '--prefix', \
                   help='Prefix for output file names [no default]', \
                   default='')
    inOpts, arguments = opt.parse_args()
    main(inOpts)
