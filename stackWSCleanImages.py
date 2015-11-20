#!/usr/bin/env python
import glob
import optparse
import pyfits as pf
import os
import numpy as np
import math

def checkBeamSize(imList):
   # Get the beam sizes of each image
   bmaj = []; bmin = []; bpa = []
   for im in imList:
      bmaj.append(pf.open(im)[0].header['BMAJ']*3600.)
      bmin.append(pf.open(im)[0].header['BMIN']*3600.)
      bpa.append(pf.open(im)[0].header['BPA'])
   bmaj = np.asarray(bmaj)
   bmin = np.asarray(bmin)
   bpa  = np.asarray(bpa)
   bmajFlag = [x == bmaj[0] for x in bmaj]
   bminFlag = [x == bmin[0] for x in bmin]
   bpaFlag = [x == bpa[0] for x in bpa]
   if all(bmajFlag) and all(bminFlag) and all(bpaFlag): return True
   else: return False

def convolImages(imList, maxBeamSize):
   outNames = []
   for im in imList:
      tempName = im.split('.fits')[0]+'.conv.fits'
      # Read in the image to miriad
      os.system('fits op=xyin in={} out=temp.im'.format(im))
      os.system('convol map=temp.im fwhm={} options=final out=temp.conv'.format(maxBeamSize))
      os.system('fits op=xyout in=temp.conv out={}'.format(tempName))
      outNames.append(tempName)
      os.system('rm -r temp.im temp.conv')
   return outNames

def getImageNoise(imList):
   print 'INFO: Estimating noise in the input images'
   noise = []; tempNoise = []
   for im in imList:
      thisData = np.squeeze(pf.open(im)[0].data).ravel()
      thisData = thisData[thisData<0]
      noise.append(np.std(thisData))
   return noise

def getWeightedSum(imList, noise):
   weights = 0
   weightedSum = 0
   for i, im in enumerate(imList):
      weightedSum += (np.squeeze(pf.open(im)[0].data) * (noise[i]**2))
      weights += noise[i]**2
   return weightedSum/weights

def main(options):
   imList = sorted(glob.glob(options.inms))
   if len(imList) == 0: raise Exception('No input fits images!')
   # Check if the input images have the same beam.
   # if they have different beam sizes, convolve to a common resolution
   if not checkBeamSize(imList):
      print 'INFO: Images have different beam shapes'
      bmaj = []
      for im in imList:
         bmaj.append(pf.open(im)[0].header['BMAJ']*3600.)
      bmaj = np.asarray(bmaj)
      maxBeamSize = np.ceil(np.max(bmaj))
      print 'INFO: Convolving to a common resolution of {} arcsec'.format(maxBeamSize)
      imList = convolImages(imList, maxBeamSize)
   # Get noise in each image
   noise = getImageNoise(imList)
   print 'Noise is', noise
   # Now compute the weighted sum
   stackedImage = getWeightedSum(imList, noise)
   # Write the image to disk
   head = pf.open(imList[0])[0].header
   hdu = pf.PrimaryHDU(data=stackedImage, header=head)
   hdu.writeto('stackedImage.fits', clobber=True)
   del hdu

if __name__ == '__main__':
   opt = optparse.OptionParser()
   opt.add_option('-i', '--inms', help='Glob string for input images', default='')
   options, arguments = opt.parse_args()
   main(options)
