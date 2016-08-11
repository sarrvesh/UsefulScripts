#!/usr/bin/env python
"""
BField.py

Computes B field map using the relation from
Beck & Krause (2005)

Written by Sarrvesh S. Sridhar.
Last updated: May 10, 2016.

"""

import optparse
import pyfits as pf
import numpy as np
from scipy.special import gamma

def main(options):
    # Get the input parameters
    iName = options.input
    thresh= float(options.blank)
    k0 = float(options.ko)
    alpha = float(options.specindex)
    i = float(options.incl)
    l = float(options.length)
    if options.f == '':
        try:
            print 'Trying to read frequency from FITS header'
            freq = pf.open(iName)[0].header['CRVAL3']
        except: raise Exception('Unable to read freq from fits header')
    
    # Compute the constants
    c_1 = 6.26428*10**18 # [erg-2 s-1 G-1]
    c_3 = np.cos(np.radians(i))
    c_2 = (1/4.) * c_3 * ((alpha+5/3.)/(alpha+1.)) * \
          gamma((3*alpha+1)/6.) * gamma((3*alpha+5)/6.)
    c = 299792458. # [m/s]
    E_p = 1.5033*10**(-3) # [erg]
    

if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option('-i', '--input', help='Input Stokes-I map [no default]',\
        default='')
    opt.add_option('-f', '--freq', help='Frequency in Hz [default: read from '+\
        'image header]', default='')
    opt.add_option('-b', '--blank', help='Blank threshold. [default: 0 Jy]',\
        default='0.0')
    opt.add_option('-k', '--ko', help='Proton to electron number density '+\
        '[default: 100]', default='100.0')
    opt.add_option('-s', '--specindex', help='Average spectral index. '+\
        '[default: -0.7]', default='-0.7')
    opt.add_option('-t', '--incl', help='Inclination angle [default=90deg]',\
        default='90')
    opt.add_option('-l', '--length', help='Synch. path length [default=1kpc]',\
        default='1')
    options, arguments = opt.parse_args()
    
    if options.input == '':
        raise Exception('Error: A valid Stokes-I map must be specified.')
    main(options)
