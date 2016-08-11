#!/usr/bin/env python
"""
findDistance.py

Prints the angular distance between a specified target
and the specified calibrator sources.

Written by Sarrvesh S. Sridhar

"""
import optparse
import glob
import pyvo as vo
from astropy.coordinates import SkyCoord
from astropy import units as u

def main(options):
    # Get the list of calibrators
    calList = options.cal.split(',')
    
    # Resolve the target
    t = vo.object2pos(options.target)
    target = SkyCoord(ra=t[0]*u.degree, dec=t[1]*u.degree)
    print "\nTarget: {} ({} {})\n".format(options.target, t[0], t[1])
    print "Calibrator\tDistance from target"
    print "==========\t===================="
    
    for cal in calList:
        try: c = vo.object2pos(cal)
        except: 
            print 'Unable to resolve target {}'.format(cal)
            continue
        calib = SkyCoord(ra=c[0]*u.degree, dec=c[1]*u.degree)
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
