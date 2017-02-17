#!/usr/bin/env python
import optparse
import pyvo as vo
from awlofar.database.Context import context
from awlofar.main.aweimports import *


def searchLofarPublicArchive(srcName, distance):
   # First get the coordinates of the source from NED
   try:
      t = vo.object2pos(srcName, db='NED')
   except:
      raise Exception('Error: Unable to resolve the specified target')
   ra  = t[0]
   dec = t[1]
   
   # Get a list of all the pointings in the LTA
   project = 'ALL'
   ok = context.set_project(project)
   obs_ids = set()
   query = (Pointing.rightAscension < (ra + distance)) &\
           (Pointing.rightAscension > (ra - distance)) &\
           (Pointing.declination    < (dec + distance))  &\
           (Pointing.declination    > (dec - distance))
   projectID = []
   for pointing in query:
      query_subarr = SubArrayPointing.pointing == pointing
      for subarr in query_subarr:
         print subarr.duration
         query_obs = Observation.subArrayPointings.contains(subarr)
         for obs in query_obs:
            if obs.numberOfSubArrayPointings <= 2 and \
               obs.numberOfBitsPerSample >= 8 and \
               obs.observingMode == 'Interferometer':
               projectID.append( obs.get_project() )
   return projectID   

if __name__ == '__main__':
   opt = optparse.OptionParser()
   opt.add_option('-s', '--source', help='A NED-compatible source name '+\
                  '[default: None]', default='')
   opt.add_option('-d', '--distance', help='Acceptable distance from '+\
                  'the pointing center in degrees [default: 1]', 
                  default=1.0)
   options, arguments = opt.parse_args()
   
   if options.source == '':
      raise Exception('Error: A valid source name must be given')

   projectID = searchLofarPublicArchive(options.source, \
                                        float(options.distance))
   print 'Found {} projects'.format(len(projectID))
   print 'Projects: ', projectID
