#!/usr/bin/env python
import optparse
from numpy import sqrt

def main(options):
   lightspeed = 299792458.
   chanWidth = float( options.chan ) * 1.E6
   centFreq  = float( options.freq ) * 1.E9
   
   part1 = (2 * lightspeed**2 * chanWidth)/(centFreq**3)
   part2 = 1. + (0.5*(chanWidth/centFreq)**2)
   delLam2 = part1 * part2
   maxPhi = sqrt(3) / delLam2
   print 'Max Faraday depth is', maxPhi

if __name__ == '__main__':
   opt = optparse.OptionParser()
   opt.add_option('-f', '--freq', help='Central frequency in GHz [default=1.5GHz]', \
                  default='1.5')
   opt.add_option('-c', '--chan', help='Channel width in MHz [default=1 MHz]', \
                  default='1')
   options, arguments = opt.parse_args()
   main(options)
