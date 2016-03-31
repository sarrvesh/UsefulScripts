#!/usr/bin/env python
import pyvo as vo
from astropy.coordinates import SkyCoord
import sys

if len(sys.argv) != 4:
   str = 'Error: Invalid command line input. '
   str += 'Run as {} <object name> <search radius in deg> <output filename>'.format(sys.argv[0])
   raise Exception(str)

objName = sys.argv[1]
radInDeg = float(sys.argv[2])
outFileName = sys.argv[3]

# Get the sources in the cut-out as a VO table 
url = 'http://vo.astron.nl/tgssadr/q/cone/scs.xml'
t = vo.conesearch(url, pos = vo.object2pos(objName), radius = radInDeg )

f = open(outFileName, 'w')
f.write("FORMAT = Name, Type, Ra, Dec, I, Q, U, V, MajorAxis, MinorAxis, Orientation, ReferenceFrequency='147610000.0', SpectralIndex='[]'\n\n")
for item in t:
   # VO table has RA and DEC in degrees. Convert it to hmsdms format
   c = SkyCoord(float(item['RA']), float(item['DEC']), unit='deg')
   newRA = c.to_string('hmsdms').split(' ')[0].replace('h',':').replace('m',':').replace('s','')
   newDec = c.to_string('hmsdms').split(' ')[1].replace('d','.').replace('m','.').replace('s','')
   # Write an entry for this source into the output file
   f.write("{name}, GAUSSIAN, {ra}, {dec}, {i}, 0, 0, 0, {ma}, {mi}, {pa}, , [-0.8]\n".format(name=item['ID'], ra=newRA, dec=newDec, i=item['Sint']/1e3, ma=item['MAJAX'], mi=item['MINAX'], pa=item['PA']))
f.close()

