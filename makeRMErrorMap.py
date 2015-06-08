#!/usr/bin/env python
"""
makeRMErrorMap.py

Compute the rotation measure error map using polarized intensity and Stokes Q or U cubes. 

Written by Sarrvesh S. Sridhar

 
"""
import optparse
try:
    import pyfits as pf
except ImportError:
    raise Exception('Unable to import pyFits')
try:
    import numpy as np
except ImportError:
    raise Exception('Unable to import Numpy.')
try:
    from scipy.constants import c as lightSpeed
except ImportError:
    raise Exception('Unable to import Scipy.')

def main(options):
    if options.qFile == '':
        raise Exception('An input Q or U file must be specified.')
    if options.freq == '':
        raise Exception('A file containing frequency list must be specified.')
    if options.polInt == '':
        raise Exception('An input polarized intensity map must be specified.')
    # If all input options are valid:
    print 'INFO: Reading the input files'
    try:
        qData   = pf.open(options.qFile)[0].data
        pData   = pf.open(options.polInt)[0].data
        header  = pf.open(options.polInt)[0].header
        freqFile = open(options.freq)
    except:
        raise Exception('Unable to read the input files.')
    print 'INFO: Image have the following dimensions:'
    print 'Stokes Q:', qData.shape
    print 'Stokes U:', pData.shape
    if qData.shape[1] != pData.shape[1] or qData.shape[2] != pData.shape[2]:
        raise Exception('Input fits have different image dimensions.')
    # Estimate the number of frequencies listed in the freq file
    freqArray   = []
    for line in freqFile:
        freqArray.append(float(line))
    print 'INFO: {:} frequencies list in the input file'.format(len(freqArray))
    if len(freqArray) != qData.shape[0]:
        raise Exception('No. of frequency channels in input files do not match.')
    # Compute variance in \lambda^2: \sigma^2_{\lambda^2}
    print 'INFO: Computing variance in lambda^2'
    freqArray    = np.asarray(freqArray)
    lambdaVals   = lightSpeed / freqArray
    lambda_pow2  = np.square(lambdaVals)
    varLambda2   = np.absolute(np.var(lambda_pow2))

    # Estimate the noise in the Q-cube along each line of sight
    print 'INFO: Estimating noise variance in Q'
    varInQ     = np.zeros(pData.shape)
    for i in range(pData.shape[1]):
        for j in range(pData.shape[2]):
            varInQ[0,i,j] = np.absolute(np.var(qData[:,i,j]))
    hdu = pf.PrimaryHDU(data=varInQ, header=header)
    hdu.writeto('varInQ.fits', clobber=True)
    del hdu
    
    # Compute the variance in RM using equation 2.73 in Brentjens' thesis
    print 'INFO: Computing variance of RM'
    denom = 4*(len(freqArray)-2) * np.square(pData) * varLambda2
    varInRM = np.absolute(np.divide(varInQ, denom))
    hdu = pf.PrimaryHDU(data=varInRM)
    hdu.writeto('varInRM.fits', clobber=True)
    del hdu
    print varInRM.shape
    
    # Compute noise in RM
    print 'INFO: Computing standard deviation in RM'
    noiseInRM = np.sqrt(varInRM)
    hdu = pf.PrimaryHDU(data=noiseInRM, header=header)
    hdu.writeto('noiseInRM.fits', clobber=True)
    del hdu

if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option('-f', '--freq', help='Frequency list', default='')
    opt.add_option('-q', '--qFile', help='Stokes Q or U file to estimate noise', default='')
    opt.add_option('-p', '--polInt', help='Polarized intensity map', default='')
    options, arguments = opt.parse_args()
    main(options)
