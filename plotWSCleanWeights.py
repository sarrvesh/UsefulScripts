#!/usr/bin/env python
"""
plotWSCleanWeights.py

Plot azimuthally averaged profiles of WSClean visibility weights.

Written by Sarrvesh S. Sridhar
Edited by George Heald
"""
import os
import argparse
import pyfits as pf
import numpy as np
import matplotlib.pyplot as plt

def main(options):
	f = np.squeeze(pf.open(options.input)[0].data)
	pixsize = float(options.pixsize)
	maxuv_ongrid = 0.5/(pixsize/206265.)
	maxuv = float(options.maxuv)
	nBins = int(options.nbin)
	binSize = maxuv/nBins
	binValues = np.arange(binSize/2.0, maxuv, binSize)
	# No. of pixels on the uv-grid along one axis
	uvGridPix = pf.open(options.input)[0].header['NAXIS1']
	# Size of a pixel on the uv-grid in lambda
	uvCellSize = (2.0 * maxuv_ongrid)/uvGridPix
	
	# Now generate the 2d uv grid from -maxuv to +maxuv
	U = np.linspace(-maxuv_ongrid, maxuv_ongrid, uvGridPix)
	V = np.linspace(-maxuv_ongrid, maxuv_ongrid, uvGridPix)
	UGrid, VGrid = np.meshgrid(U, V)
	# Determine how far away a given cell is from (u=0, v=0)
	uvDist = np.sqrt(np.add(np.square(UGrid), np.square(VGrid)))

    # Compute azimuthally averaged weights for each bin
	radialProfile = []
	for val in binValues:
		thisMin = (val - (binSize/2.0))
 		thisMax = (val + (binSize/2.0))
		print 'Bin range: {} {}'.format(thisMin, thisMax)
		f_inbin = f[np.logical_and(uvDist<=thisMax,uvDist>thisMin)].flatten()
		print 'Found {} pixels in this bin'.format(len(f_inbin))
		radialProfile.append( np.sum(f_inbin) / len(f_inbin) )
	radialProfile = np.asarray(radialProfile)
	# Plot the profile
	plt.plot(binValues, radialProfile, 'b*')
	plt.savefig(options.output, bbox_inches='tight')

if __name__ == '__main__':
	opt = argparse.ArgumentParser()
	opt.add_argument('input', help='Input weights file [no default]',\
            default='')
	opt.add_argument('-m', '--maxuv', help='Max UV in lambda specified while imaging [no default]',\
            default='')
	opt.add_argument('-p', '--pixsize', help='Pixel size in arcsec specified while imaging [no default]',\
            default='')
	opt.add_argument('-n', '--nbin', help='No. of bins to plot [default: 10]',\
            default='10')
	opt.add_argument('-o', '--output', help='Output file name [default: profile.png]',\
            default='profile.png')
	options = opt.parse_args()
	if options.input == '':
		raise Exception('Invalid input')
	if options.maxuv == '':
		raise Exception('You need to set --maxuv or -m')
	if options.pixsize == '':
		raise Exception('You need to set --pixsize or -p')
	main(options)

