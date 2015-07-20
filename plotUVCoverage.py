#!/usr/bin/env python
"""
plotUVCoverage.py

This script plots the uv-coverage of a given measurement set.

Written by Sarrvesh S. Sridhar

TODO: 
* Average in time and frequency before plotting
"""
import optparse
import sys
import pyrap.tables as pt
import matplotlib.pyplot as plt   

def main(options):
    # Open the input measurement set
    ms = pt.table(options.msin, readonly=True, ack=False)
    # Get the time footprint of the measurement set
    startTime = ms.getcell('TIME', 0)
    endTime   = ms.getcell('TIME', ms.nrows()-1)
    intTime   = ms.getcell('INTERVAL', 0)
    nTimeSlots= (endTime - startTime)/intTime
    # Get the u and v entries from the UVW column
    uCol = ms.getcol('UVW')[:,0]/1000.
    vCol = ms.getcol('UVW')[:,1]/1000.
    plt.scatter(uCol, vCol, marker='.')
    plt.xlabel('U (km)')
    plt.ylabel('V (km)')
    plt.show()

if __name__ == '__main__':
    opt=optparse.OptionParser()
    opt.add_option('-m', '--msin', help='Input measurement set [no default]',
                   default='')
    inOpts, arguments = opt.parse_args()
    main(inOpts)
