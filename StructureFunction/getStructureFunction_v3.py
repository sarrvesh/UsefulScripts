#!/usr/bin/env python
###################################################################################
##
## Ver 3: Subtract DC offset estimated from standard deviation in RM
##
###################################################################################
import optparse
import time
import os
import sys
try:
    import pyfits as pf
except ImportError:
    raise Exception('Error: Pyfits is not installed!')
try:
    from pywcs import WCS
except ImportError:
    raise Exception('Error: Pywcs is not installed!')
try:
	import matplotlib.pyplot as plt
except ImportError:
	raise Exception('Error: Matplotlib.pyplot is not installed!')
import numpy as np

t = time.time()

def main(options):
    
    # Some filenames used within the script
    maskedImFile       = 'maskedFD.FITS'
    validPixelFileName = 'validPixelList.txt'
    maskedRMErrMap     = 'maskedRMErrorMap.FITS'
    plotValsFromC      = 'plotPoints.txt'
    
    # Remove all temp files from previous execution
    print 'INFO: Cleaning up the workspace'
    os.system('rm {} {} {} {}'.format(maskedImFile, validPixelFileName, maskedRMErrMap, plotValsFromC))
    
    if options.fdImage == '':
        raise Exception('Faraday Depth image was not specified.')
    if options.rmError == '':
        raise Exception('An RM Error map must be specified.')
    if options.threshold == '' or options.polInt == '':
        print 'INFO: A valid mask was not specified.'
        print 'INFO: All pixels will be included for computing structure function.'
        # Read in the Faraday depth image
        try: 
            fdImage = pf.open(options.fdImage)
            errImage= pf.open(options.rmError)
        except: raise Exception('Unable to read the input image.')
        fdArray = fdImage[0].data
        errArray= errImage[0].data
        header  = fdImage[0].header
        fdImage.close()
        # Loop over each pixel and get the sky coordinates
        wcs     = WCS(header)
        raSize  = fdArray.shape[-1]
        decSize = fdArray.shape[-2]
        tempRA = []; dec = []; RM = []; errRM = []
        for i in range(raSize):
            for j in range(decSize):
            	# Do not include blanked pixels. Pywcs reads them as nan
            	if str(fdArray[i,j]) == 'nan': continue
            	else:
                    tempRA.append(wcs.wcs_pix2sky([[i,j,0]], 0)[0][0])
                    dec.append   (wcs.wcs_pix2sky([[i,j,0]], 0)[0][1])
                    RM.append    (fdArray[i,j])
                    errRM.append (errArray[i,j])
        nValidPixels = len(dec)
    else:
        # Use Pol Int image to select valid pixels
        try:
            fdImage = pf.open(options.fdImage)
            iImage  = pf.open(options.polInt)
            errImage= pf.open(options.rmError)
        except: raise Exception('Unable to read the input images')
        fdArray = fdImage[0].data
        iArray  = iImage[0].data
        errArray= errImage[0].data
        header  = fdImage[0].header
        #Initialize a new array which will be updated as per the mask
        maskedIm= fdImage[0].data
        maskerrRM = errImage[0].data
        # Check if the input images have the same shape
        if fdArray.shape != iArray.shape:
            raise Exception('Input images have different shape')
        wcs    = WCS(header)
        raSize = fdArray.shape[-1]
        decSize= fdArray.shape[-2]
        tempRA = []; dec = []; RM = []; errRM = []
        nValidPixels = 0
        for i in range(raSize):
            for j in range(decSize):
                if iArray[i,j] < float(options.threshold):
                    maskedIm[i,j] = np.nan
                    maskerrRM[i,j] = np.nan
                else:
                    tempRA.append(wcs.wcs_pix2sky([[i,j,0]], 0)[0][0])
                    dec.append   (wcs.wcs_pix2sky([[i,j,0]], 0)[0][1])
                    RM.append    (fdArray[i,j])
                    errRM.append (errArray[i,j])
                    nValidPixels += 1
        print 'INFO: Selected {:} of {:} pixels'.format(nValidPixels, raSize*decSize)
        # Write out the masked image to disk
        print 'INFO: Writing out the masked to disk'
        hdu = pf.PrimaryHDU(data=maskedIm, header=header)
        hdu.writeto(maskedImFile)
        hdu = pf.PrimaryHDU(data=maskerrRM, header=header)
        hdu.writeto(maskedRMErrMap)
    # If this data set is from WSRT, add 360 to RA
    if options.isWSRT:
        ra = [val+360. for val in tempRA]
    else:
        ra = tempRA
    
    # Write (ra, dec, RM, eRM) to disk
    tempFile = open(validPixelFileName, 'w')
    for i in range(len(ra)):
        tempFile.write('{:.5f} {:.5f} {:.5f} {:.5f}\n'.format(ra[i], dec[i], RM[i], errRM[i]))
    tempFile.close()
    
    # Pass the pixel list and the number of entries to the C code
    os.system('./computeStructureFunction {:} {:} {} {} {} {}'.format(\
              validPixelFileName, nValidPixels, options.binStart,  \
              options.nBins, options.binSize, plotValsFromC))
    # Read the plot points returned by C
    xVal = []; diffVal = []; rmVal = []; eRMVal = []
    for line in open(plotValsFromC, "r"):
    	xVal.append   (float(line.split()[0]))
    	rmVal.append  (float(line.split()[1]))
    	eRMVal.append (float(line.split()[2]))
    xVal   = np.asarray(xVal)
    rmVal  = np.asarray(rmVal)
    eRMVal = np.asarray(eRMVal)
    diffVal= np.subtract(rmVal, eRMVal)
    
    # Plot
    plt.plot(xVal, np.log10(diffVal), 'bo', label="My code")
    #plt.plot(xVal, rmVal  , color='blue')
    #plt.plot(xVal, eRMVal , color='purple')
    plt.xlabel('Angular distance (deg)')
    plt.ylabel('Structure function')
    #plt.show()
    
    # Plot Ann's values on yours
    annX = []; annRM = []; annERM = []
    for line in open('structure_function_Lband.dat',"r"):
    	annX.append(float(line.split()[0]))
    	annRM.append(float(line.split()[1]))
    	annERM.append(float(line.split()[2]))
    annX = np.asarray(annX)
    annRM= np.asarray(annRM)
    annERM=np.asarray(annERM)
    annDiff = np.subtract(annRM, annERM)
    plt.plot(np.log10(annX), np.log10(annDiff), 'ro', label="Ann's code")
    plt.legend(loc='best')
    plt.show()
    
print ''
opt = optparse.OptionParser()
opt.add_option('-p', '--polInt', help='Polarized Intensity image to use as a mask [no default]', default='')
opt.add_option('-t', '--threshold', help='Threshold level as mask [no default]', default='')
opt.add_option('-f', '--fdImage', help='Faraday depth map [no default]', default='')
opt.add_option('-e', '--rmError', help='RM Error Map [no default]',default='')
opt.add_option('-w', '--isWSRT', help='Enable this flag to indicate the data is from WSRT', \
               action='store_true')
opt.add_option('-b', '--binStart', help='Minimum value to start binning [default:-2.5]', default='-2.5')
opt.add_option('-n', '--nBins', help='No of bins [default: 20]', default='20')
opt.add_option('-s', '--binSize', help='Size of a bin [default: 0.1]', default='0.1')
options, arguments = opt.parse_args()
main(options)

# Execution time
print 'Processing time:', (time.time() - t)/60., 'minutes'
print ''
