#!/usr/bin/env python
"""
listDataCols.py

List the data columns in the input measurement set.
Assumes that data columns are the only ones with type COMPLEX.

Written by Sarrvesh S. Sridhar

To Do:
======
* Accept multiple measurement sets as input
* Is there another way to check if a given column contains visibilities?
"""
try:
    import pyrap.tables as pt
except ImportError:
    raise Exception('Unable to import Pyrap.')
import optparse

def main(options):
    # Read in the input measurement
    try:
    	ms = pt.table(options.msin, readonly=True, ack=False)
    except:
    	raise Exception('Unable to read the specified measurement set.')
    # Get the list of columns in this measurement set
    colList = ms.colnames()
    # Print columns containing visibilities
    print '\nColumns in {}:'.format(options.msin.split('/')[-1])
    for column in colList:
	   	if ms.getcoldesc(column)['valueType'] == 'complex':
	   		print column
    # Close the measurement set
    ms.close()
    print ''

if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option('-m', '--msin', help='Input measurement set [no default]',\
                   default='')
    options, arguments = opt.parse_args()
    main(options)
