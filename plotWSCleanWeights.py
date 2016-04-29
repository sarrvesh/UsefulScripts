#!/usr/bin/env python
"""
plotWSCleanWeights.py

Plot azimuthally averaged profiles of WSClean visibility weights.

Written by Sarrvesh S. Sridhar
"""
import os
import optparse
import pyfits as pf
import numpy as np
import matplotlib.pyplot as plt

def main(options):
	f = np.squeeze(pf.open(options.input)[0].data)
	maxuv = float(options.maxuv)
	nBins = int(options.nbin)
	binSize = maxuv/nBins
	binValues = np.arange(binSize/2.0, maxuv, binSize)
	# No. of pixels on the uv-grid along one axis
	uvGridPix = pf.open(options.input)[0].header['NAXIS1']
	# Size of a pixel on the uv-grid in lambda
	uvCellSize = (2.0 * maxuv)/uvGridPix
	
	# Now generate the 2d uv grid from -maxuv to +maxuv
	U = np.linspace(-maxuv, maxuv, uvGridPix)
	V = np.linspace(-maxuv, maxuv, uvGridPix)
	UGrid, VGrid = np.meshgrid(U, V)
	# Determine how far away a given cell is from (u=0, v=0)
	uvDist = np.sqrt(np.add(np.square(UGrid), np.square(VGrid)))

    # Compute azimuthally averaged weights for each bin
	radialProfile = []
	for val in binValues:
		print 'Bin range: {} {}'.format(val - (binSize/2.0), val + (binSize/2.0))
		thisMin = (val - (binSize/2.0)) * np.ones_like(uvDist)
 		thisMax = (val + (binSize/2.0)) * np.ones_like(uvDist)
		tempWeight = np.empty_like(f)
		tempWeight[:] = f
		# Mask all pixels that do not fall within this ring
		tempWeight[np.greater(uvDist, thisMax)] = 0
		tempWeight[np.less(uvDist, thisMin)] = 0
		# Find the sum of all non-zero pixels
		print 'Found {} pixels in this bin'.format(np.count_nonzero(tempWeight))
		radialProfile.append( np.sum(tempWeight) / np.count_nonzero(tempWeight) )
	radialProfile = np.asarray(radialProfile)
	# Plot the profile
	plt.plot(binValues, radialProfile, 'b*')
	plt.savefig(options.output, bbox_inches='tight')

if __name__ == '__main__':
	opt = optparse.OptionParser()
	opt.add_option('-i', '--input', help='Input weights file [no default]',\
            default='')
	opt.add_option('-m', '--maxuv', help='Max UV in lambda specified while imaging [no default]',\
            default='')
	opt.add_option('-n', '--nbin', help='No. of bins to plot [default: 10]',\
            default='10')
	opt.add_option('-o', '--output', help='Output file name [default: profile.png]',\
            default='profile.png')
	options, arguments = opt.parse_args()
	if options.input == '':
		raise Exception('Invalid input')
	if options.maxuv == '':
		raise Exception('You need to set --maxuv or -m')
	main(options)
