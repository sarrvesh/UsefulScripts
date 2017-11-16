#!/usr/bin/env python
"""
getRMSF.py

This script plots the Rotation Measure Spread Function for a given
list of frequencies.

Written by Sarrvesh S. Sridhar

To do:
* Include weights
"""
import sys
import optparse
try:
    from numpy import median, zeros, exp, absolute, amin, amax, sqrt, pi
except ImportError:
    raise Exception('Unable to import Numpy.')
try:
    import matplotlib.pyplot as plt
except ImportError:
    raise Exception('Unable to import Matplotlib.')
c = 299792458. # [m/s]

def main(options):
    # Get the user input
    freqFile = options.freq
    minPhi   = float(options.minphi)
    delPhi   = float(options.delphi)
    nPhi     = int(options.nphi)
    
    # Read the list of frequencies
    lam2 = []
    with open(freqFile) as f:
        for line in f:
    	    lam2.append( (c/float(line))**2 )
    
    # Compute \lambda_0^2
    lam2_0 = median(lam2)
    
    # Get the normalization factor K
    K = 0
    for i in lam2:
        K += 1
    
    # Compute the numerator of R(\phi)
    maxPhi		= minPhi + delPhi*(nPhi-1)
    absR  		= []
    realR 		= []
    imagR 		= []
    phiArray 	= []
    phi     	= minPhi
    while phi < maxPhi:
	    phiArray.append(phi)
	    tempR = 0 + 0j
	    for i in range(len(lam2)):
	    	tempR += exp(-2*1j*phi*(lam2[i]-lam2_0))
	    absR.append( absolute(tempR)/K )
	    realR.append( tempR.real/K )
	    imagR.append( tempR.imag/K )
	    phi += delPhi
    
    # Print stats
    fwhm 	= 3.8 / (amax(lam2)-amin(lam2)) # from Schnitzeler et al (2008)
    maxSize = pi/amin(lam2)
    print '\nFor a top-hat weight function:\n'
    print '\tFWHM: '+str(fwhm)+' rad/m2'
    print '\tMax scale: '+str(maxSize)+' rad/m2 \n'
    
    # Make plots
    plt.plot(phiArray,absR,'black',label='|R|')
    plt.plot(phiArray,realR,'r--',label='real(R)')
    plt.plot(phiArray,imagR,'b--',label='imag(R)')
    plt.xlabel('Faraday depth [rad/m^2]')
    plt.ylabel('RMSF')
    plt.legend()
    plt.savefig('rmsf.png')

if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option('-f', '--freq', help='Text file containing the frequency '+
            'list [no default]', default='')
    opt.add_option('-m', '--minphi', help='Minimum Faraday depth [default: -50 rad/m2]',
             default='-50')
    opt.add_option('-d', '--delphi', help='Delta Faraday depth [default: 1 rad/m2]',
             default='1')
    opt.add_option('-n', '--nphi', help='Number of values to compute [default: 100]',
             default='100')
    inOpts, arguments = opt.parse_args()
    main(inOpts)
