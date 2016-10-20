#!/usr/bin/env python
"""


For a given HI moment-0 map, the script computes the HI surface mass density
using the relation from Leroy et al (2008). The script assumes that the pixel values have unit K.km/s

Written by Sarrvesh S. Sridhar
"""
import pyfits as pf
import optparse
from numpy import cos, radians

def main(options):
   # Get the pixel values and header
   data = pf.open(options.input)[0].data
   head = pf.open(options.input)[0].header

   # Check if BUNIT has Jy in it
   if 'jy' in head['BUNIT'].lower():
      raise IOError('Units should be in K.km/s')

   # Do the actual calculation
   print 'INFO: Assuming pixels are in K.km/s'
   sigma_hi = 0.015*cos(radians(float(options.inc)))*data

   # Write out the fits files
   head['BUNIT'] = 'Msolar pc^-2'
   hdu = pf.PrimaryHDU(data=data, header=head)
   hdu.writeto(options.out)

if __name__ == '__main__':
   opt = optparse.OptionParser()
   opt.add_option('-f', '--input', help='Input image [no default]', default='')
   opt.add_option('-o', '--out', help='Output image [no default]', default='')
   opt.add_option('-i', '--inc', help='Inclination angle [no default]')
   options, arguments = opt.parse_args()
   main(options)
