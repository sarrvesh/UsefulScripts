#!/usr/bin/env python
###########################################################
#
# Make a CLEAN mask using LOFAR restored and residual maps
# Not very user-friendly at the moment.
#
###########################################################
import pyrap.images as pim
from pyrap import quanta
import glob
import pyfits as pf
import os
import numpy as np
import lofar.bdsm as bdsm

smoothSize = 30.0

sbList = [160]
for sb in sbList:
	# Get the beam shape from the restored image
	this_pim = pim.image(glob.glob('SB{:03d}*.restored'.format(sb))[0])
	info_dict = this_pim.info()['imageinfo']['restoringbeam']
	bpar_ma = quanta.quantity(info_dict['major']).get_value('deg')*3600.
	bpar_mi = quanta.quantity(info_dict['minor']).get_value('deg')*3600.
	bpar_pa = quanta.quantity(info_dict['positionangle']).get_value('deg')
	
	# Convert the restored and the restored.corr to fits
	restored = 'SB{:03d}_restored.fits'.format(sb)
	restoredCorr = 'SB{:03d}_restored.corr.fits'.format(sb)
	t = pim.image(glob.glob('SB{:03d}*restored'.format(sb))[0])
	t.tofits(restored)
	t = pim.image(glob.glob('SB{:03d}*restored.corr'.format(sb))[0])
        t.tofits(restoredCorr)

	# Convert the residual image to fits file including the beam
	residual = 'SB{:03d}_residual.fits'.format(sb)
	t = pim.image(glob.glob('SB{:03d}*residual'.format(sb))[0])
        t.tofits('temp.fits')
	os.system('fits op=xyin in=temp.fits out=temp')
	os.system('puthd in=temp/bmaj value={},"arcseconds"'.format(bpar_ma))
	os.system('puthd in=temp/bmin value={},"arcseconds"'.format(bpar_mi))
	os.system('puthd in=temp/bpa value={},"degrees"'.format(bpar_pa))
	os.system('puthd in=temp/bunit value="Jy/Beam"')
	os.system('prthd in=temp')
	os.system('convol map=temp options=final fwhm={} out=temp.conv'.format(smoothSize))
	os.system('fits op=xyout in=temp.conv out={}'.format(residual))
	os.system('rm -r temp temp.conv')

        # Convert the residual.corr image to fits file including the beam
        residualCorr = 'SB{:03d}_residual.corr.fits'.format(sb)
        t = pim.image(glob.glob('SB{:03d}*residual.corr'.format(sb))[0])
        t.tofits('temp.fits')
        os.system('fits op=xyin in=temp.fits out=temp')
        os.system('puthd in=temp/bmaj value={},"arcseconds"'.format(bpar_ma))
        os.system('puthd in=temp/bmin value={},"arcseconds"'.format(bpar_mi))
        os.system('puthd in=temp/bpa value={},"degrees"'.format(bpar_pa))
        os.system('puthd in=temp/bunit value="Jy/Beam"')
        os.system('prthd in=temp')
        os.system('convol map=temp options=final fwhm={} out=temp.conv'.format(smoothSize))
        os.system('fits op=xyout in=temp.conv out={}'.format(residualCorr))
        os.system('rm -r temp temp.conv t.fits')

	# Run pybdsm on the residual images
	residualMask = 'mask_{:03d}.residual.fits'.format(sb)
	img = bdsm.process_image(residual, adaptive_rms_box=True, advanced_opts=True, \
			   detection_image=residualCorr, ini_method='curvature', atrous_do=True, \
			   psf_vary_do=False, thresh_isl=6.0, thresh_pix=8.0, \
			   beam=(smoothSize/3600.,smoothSize/3600.,0.))
	img.export_image(outfile=residualMask, img_type='island_mask', img_format='fits', clobber=True)
	img.export_image(outfile=residualMask+'.casa', img_type='island_mask', img_format='casa', clobber=True)

	# Run pybdsm on the residual images
        restoredMask = 'mask_{:03d}.restored.fits'.format(sb)
	img = bdsm.process_image(restored, adaptive_rms_box=True, advanced_opts=True, \
                           detection_image=restoredCorr, ini_method='curvature', atrous_do=True, \
                           psf_vary_do=True, thresh_isl=6.0, thresh_pix=8.0)
	img.export_image(outfile=restoredMask, img_type='island_mask', img_format='fits', clobber=True)
	img.export_image(outfile=restoredMask+'.casa', img_type='island_mask', img_format='casa', clobber=True)

	# Merge the residual and the restored masks
	a = pim.image(restoredMask+'.casa')
	b = pim.image(residualMask+'.casa')
	aData = a.getdata()
	bData = b.getdata()
	newMask = np.logical_or(aData, bData).astype(float, casting='safe')
	print newMask.dtype
	a.putdata(newMask)
	a.saveas('SB{:03d}.finalMask.casa'.format(sb))
	a.tofits('SB{:03d}.finalMask.fits'.format(sb))
