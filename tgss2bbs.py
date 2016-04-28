#!/usr/bin/env python
"""
tgss2bbs.py

This script sources from the TGSS VO server and creates a BBS compatible skymodel.

Written by Sarrvesh S. Sridhar.
Updated by George Heald.
Last updated: April 28, 2016.

"""
import pyvo as vo
from astropy.coordinates import SkyCoord
import optparse

def main(options):
   objName = options.srcID
   radInDeg = float(options.radius)
   outFileName = options.output
   inOnePatch = options.patch

   # Get the sources in the cut-out as a VO table 
   url = 'http://vo.astron.nl/tgssadr/q/cone/scs.xml'
   t = vo.conesearch(url, pos = vo.object2pos(objName), radius = radInDeg )

   f = open(outFileName, 'w')
   if options.patch:
      # Write all selected components as a single patch
      f.write("FORMAT = Name, Type, Patch, Ra, Dec, I, Q, U, V, MajorAxis, MinorAxis, Orientation, ReferenceFrequency='147610000.0', SpectralIndex='[]'\n\n")
      # Get the coordinates of the source
      c = SkyCoord(float(vo.object2pos(objName)[0]), float(vo.object2pos(objName)[1]), unit='deg')
      newRA = c.to_string('hmsdms').split(' ')[0].replace('h',':').replace('m',':').replace('s','')
      newDec = c.to_string('hmsdms').split(' ')[1].replace('d','.').replace('m','.').replace('s','')
      # Create the patch
      f.write(' , , Patch, {ra}, {dec}\n'.format(ra=newRA, dec=newDec))
      for item in t:
         # VO table has RA and DEC in degrees. Convert it to hmsdms format
         c = SkyCoord(float(item['RA']), float(item['DEC']), unit='deg')
         newRA = c.to_string('hmsdms').split(' ')[0].replace('h',':').replace('m',':').replace('s','')
         newDec = c.to_string('hmsdms').split(' ')[1].replace('d','.').replace('m','.').replace('s','')
	 # Determine whether source is extended
	 sratio = item['Sint']/item['Spk']
	 if sratio > 1.25:
		srctype='GAUSSIAN'
		majaxsize = (max([item['MAJAX'],25.])**2-25.**2)**0.5
		minaxsize = (max([item['MINAX'],25.])**2-25.**2)**0.5
	 else:
		srctype='POINT'
		majaxsize = ""
		minaxsize = ""
         # Write an entry for this source into the output file inside the above defined patch
         f.write("{name}, {type}, Patch, {ra}, {dec}, {i}, 0, 0, 0, {ma}, {mi}, {pa}, , [-0.8]\n".format(name=item['ID'], type=srctype, ra=newRA, dec=newDec, i=item['Sint']/1e3, ma=majaxsize, mi=minaxsize, pa=item['PA']))
   else:
      # Writes sources without a patch
      f.write("FORMAT = Name, Type, Ra, Dec, I, Q, U, V, MajorAxis, MinorAxis, Orientation, ReferenceFrequency='147610000.0', SpectralIndex='[]'\n\n")
      for item in t:
         # VO table has RA and DEC in degrees. Convert it to hmsdms format
         c = SkyCoord(float(item['RA']), float(item['DEC']), unit='deg')
         newRA = c.to_string('hmsdms').split(' ')[0].replace('h',':').replace('m',':').replace('s','')
         newDec = c.to_string('hmsdms').split(' ')[1].replace('d','.').replace('m','.').replace('s','')
	 # Determine whether source is extended
	 sratio = item['Sint']/item['Spk']
	 if sratio > 1.25:
		srctype='GAUSSIAN'
		majaxsize = (max([item['MAJAX'],25.])**2-25.**2)**0.5
		minaxsize = (max([item['MINAX'],25.])**2-25.**2)**0.5
	 else:
		srctype='POINT'
		majaxsize = ""
		minaxsize = ""
         # Write an entry for this source into the output file
         f.write("{name}, {type}, {ra}, {dec}, {i}, 0, 0, 0, {ma}, {mi}, {pa}, , [-0.8]\n".format(name=item['ID'], type=srctype, ra=newRA, dec=newDec, i=item['Sint']/1e3, ma=majaxsize, mi=minaxsize, pa=item['PA']))
   f.close()

if __name__ == '__main__':
   opt = optparse.OptionParser()
   opt.add_option('-s', '--srcID', help='Resolveable source name [no default]', default='')
   opt.add_option('-r', '--radius', help='Search radius in deg [default: 5.0 deg]', default='5.0')
   opt.add_option('-o', '--output', help='Output filename [default: tgss.skymodel]', default='tgss.skymodel')
   opt.add_option('-p', '--patch', help='Write all sources as a single patch? [default: True]', action='store_true')
   options, arguments = opt.parse_args()
   
   if options.srcID == '':
      raise Exception('Error: A valid source name must be given.')
   main(options)
