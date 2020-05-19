#!/usr/bin/env python
"""
findDistance.py

Prints the angular distance between a specified target
and the specified calibrator sources.

Written by Sarrvesh S. Sridhar

"""
import optparse
import glob
from astropy.coordinates import SkyCoord
from astropy import units as u
import sys

def main(options):
    # Get the list of calibrators
    calList = options.cal.split(',')
    
    # Resolve the target
    print options.target
    try: t = SkyCoord.from_name(options.target)
    except:
       print 'Unable to query the target. Terminating execution'
       sys.exit(1)
    target = t
    print "\nTarget: {} ({} {})\n".format(options.target, t.ra, t.dec)
    print "Calibrator\tDistance from target"
    print "==========\t===================="
    
    for cal in calList:
        try: c = SkyCoord.from_name(cal)
        except: 
            print 'Unable to resolve target {}'.format(cal)
            continue
        calib = c
        distance = target.separation(calib)
        print "{}\t{}".format(cal, distance)

if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option('-t', '--target', help='Target name [no default]', \
                   default='')
    opt.add_option('-c', '--cal', help='Comma-separated list of calibrators '+\
                   '[default:3C295,3C147]', default='3C295,3C147')
    options, arguments = opt.parse_args()
    main(options)
