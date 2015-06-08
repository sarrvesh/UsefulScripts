makeFitsCube
============
Concats a list of 2D fits images into a 4D cube. Handy for running RM Synthesis.

Usage: makeFitsCube.py [options]

Options:
  -h, --help         show this help message and exit
  -i INP, --inp=INP  Glob selection string for input files [no default]
  -o OUT, --out=OUT  Filename of the output cube [default: mergedFits.fits]
  -f, --freq         Write the list of frequencies to a text file [default: False]

Dependencies:
* psutil (https://github.com/giampaolo/psutil)
* pyFits (http://www.stsci.edu/institute/software_hardware/pyfits)
* Numpy (http://www.numpy.org/)

To Do:
* Use AstroPy instead of pyFits.
