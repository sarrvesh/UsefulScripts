#!/usr/bin/env python
"""
genSurveyTxt.py

Script to automatically generate observation setup (text) files for the
Tier-1 survey that can then be converted into an XML file.

Version 0.1 written 14/11/2017 by Sarrvesh S. Sridhar
"""
import optparse
import datetime
try:
    from astropy.coordinates import SkyCoord
    import astropy.units as u
except ImportError:
    raise Exception('\nError: Astropy module not found. Install with'+\
                    ' "pip install astropy --user" for example')
import numpy as np
try:
    from ephem import Observer, FixedBody, degrees, separation, Sun
except ImportError:
    raise Exception('\nError: Ephem module not found. Install with'+\
                    ' "pip install ephem --user" for example')

class PointingInfo(object):
    """
    Everything about a pointing is retained in this class.

    Attributes:
        projectName:     Same as the proposal code.
        mainName:        Main folder name.
        startTime:       Start time of the observing block.
        targetObsLength: Length of the target scan.
        aTeamSources:    Sources that need to be demixed.
        elevation:       Minimum source elevation.
        avg:             Freq and time averaging parameters.
        namePoint1:      Name of the first target beam.
        namePoint2:      Name of the second target beam.
        coordPoint1:     RA, Dec of the first target beam.
        coordPoint2:     RA, Dec of the second target beam.
        validCals:       List of valid flux density calibrators
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, options):
        """
        Parse user input and extract relevant information
        """
        self.projectName = options.project
        self.mainName = options.main_name
        try:
            dy, dm, ds, th, tm, ts = options.date.split('-')
            self.startTime = datetime.datetime(int(dy), int(dm), int(ds), \
                                               int(th), int(tm), int(ts))
        except:
            raise IOError('Invalid date specified.')
        self.targetObsLength = float(options.time)
        self.aTeamSources = options.demix.split(',')
        self.elevation = float(options.elevation)
        self.avg = options.avg
        try:
            self.namePoint1 = options.point1.split(',')[0]
            self.namePoint2 = options.point2.split(',')[0]
            self.coordPoint1 = SkyCoord('{} {}'.format(\
                                        options.point1.split(',')[1],\
                                        options.point1.split(',')[2]), \
                                        unit=(u.hourangle, u.deg))
            self.coordPoint2 = SkyCoord('{} {}'.format(\
                                        options.point2.split(',')[1],\
                                        options.point2.split(',')[2]), \
                                        unit=(u.hourangle, u.deg))
        except IndexError:
            raise IOError('Invalid pointing format specified.')

        # Define all parameters that are common to both cal and target blocks
        self.commonStr = "split_targets=F\ncalibration=none\n"\
                "processing=Preprocessing\n"\
                "imagingPipeline=none\ncluster=CEP4\nrepeat=1\n"\
                "nr_tasks=122\nnr_cores_per_task=2\npackageDescription="\
                "HBA Dual Inner, 110-190MHz, 8bits, 48MHz@144MHz, 1s,"\
                " 64ch/sb\nantennaMode=HBA Dual Inner\nclock=200 MHz\n"\
                "instrumentFilter=110-190 MHz\nnumberOfBitsPerSample=8\n"\
                "integrationTime=1.0\nchannelsPerSubband=64\n"\
                "stationList=all\ntbbPiggybackAllowed=T\n"\
                "aartfaacPiggybackAllowed=T\ncorrelatedData=T\n"\
                "coherentStokesData=F\nincoherentStokesData=F\nflysEye=F\n"\
                "coherentDedisperseChannels=False\n"\
                "flaggingStrategy=HBAdefault\nGlobal_Subbands=104..136,"\
                "138..163,165..180,182..184,187..209,212..213,215..240,"\
                "242..255,257..273,275..300,302..328,330..347,349,364,372,"\
                "380,388,396,404,413,421,430,438,447;243\n"\
                "timeStep1=60\ntimeStep2=60"

        # Make a list of all valid calibrators
        self.validCals = ['3C295', '3C196', '3C48', '3C147', '3C380']

    def validateInput(self):
        """
        Validate user input for
        - valid project and main folder names
        """
        self.validateNames()
        self.validateDemix()
        self.validatePointings()
        self.distanceToSun()

    def validatePointings(self):
        """
        Make sure that the two pointings are inside the tile beam.
        """
        if self.coordPoint1.separation(self.coordPoint2).deg > 8.:
            raise IOError('Angular separation between the two target '+\
                          'beams is more than 8 degrees.')

    def validateNames(self):
        """
        Check if the specified project names are valid
        """
        if self.projectName == '':
            raise IOError('You must specify a valid project name.')
        elif len(self.projectName) != 7:
            raise IOError('Specified project name is invalid.')
        elif len(self.mainName) > 20:
            raise IOError('main_name cannot be more than 20 '+\
                          'characters long')

    def validateDemix(self):
        """
        Check if the A-team source information is valid.
        """
        validATeam = ['CasA', 'CygA', 'TauA', 'VirA']
        if len(self.aTeamSources) > 2:
            raise IOError('Cannot demix more than two sources.')
        if self.avg != '4,1':
            print 'INFO: Specified averaging is different from Tier-1 '+\
                  'specifications. Specified averaging will be applied '+\
                  'only to the user\'s target field.'
        for item in self.aTeamSources:
            if item not in validATeam:
                raise IOError('Invalid A-team source specified.')

    def makeHeader(self, outFile):
        """
        Write the header section to the output text file
        """
        outFile.write('projectName={}\n'.format(self.projectName))
        outFile.write('mainFolderName={}\n'.format(self.mainName))
        outFile.write('mainFolderDescription=Preprocessing:HBA Dual Inner,'+\
                      ' 110-190MHz, 8bits, 48MHz@144MHz, 1s, 64ch/sb\n\n')

    def writeCalibrator(self, startTime, calibName, outFile):
        """
        Write the calibrator section
        """
        outFile.write('BLOCK\n\n')
        outFile.write('packageName={}\n'.format(calibName))
        outFile.write('startTimeUTC={}\n'.format(startTime.isoformat(' ')))
        outFile.write('targetDuration_s=600\n')
        outFile.write(self.commonStr+'\n')
        outFile.write('targetBeams=\n')
        outFile.write('{};{};;;;;T;1800\n'.format(getCalPointing(calibName),\
                      calibName))
        outFile.write('Demix=4;1;64;10;;;F\n')
        outFile.write('\n')

        # Return the start time for the next block
        return startTime + datetime.timedelta(minutes=11)

    def writeTarget(self, startTime, outFile):
        """
        Write the target block.
        """
        outFile.write('BLOCK\n\n')
        outFile.write('packageName={}-{}\n'.format(self.namePoint1,
                                                   self.namePoint2))
        outFile.write('startTimeUTC={}\n'.format(startTime.isoformat(' ')))
        outFile.write('targetDuration_s={}\n'.format(int(\
                      self.targetObsLength*3600.)))
        outFile.write(self.commonStr+'\n')
        outFile.write('targetBeams=\n')
        # Compute the tile beam reference
        refCoord = self.getTileBeam()
        # Write the tile beam
        outFile.write('{};REF;256;1;;;F;31200\n'\
                      .format(refCoord.to_string(style='hmsdms', sep=':')\
                      .replace(' ', ';')))
        # Write the user pointing
        if self.aTeamSources == '':
            demix = ''
        else:
            demix = '{}'.format(self.aTeamSources)
            demix = demix.replace("'", '').replace(' ', '')
        outFile.write('{};{};;;;;T;31200\n'.format(\
                      self.coordPoint1.to_string(style='hmsdms', sep=':')\
                      .replace(' ', ';'), self.namePoint1))
        outFile.write('Demix={};64;10;;{};F\n'.format(\
                      self.avg.replace(',', ';'), demix))
        # Write the tier-1 pointing
        outFile.write('{};{};;;;;T;31200\n'.format(\
                      self.coordPoint2.to_string(style='hmsdms', sep=':')\
                      .replace(' ', ';'), self.namePoint2))
        outFile.write('Demix=4;1;64;10;;;F\n')
        outFile.write('\n')
        # Return the start time for the next block
        return startTime + datetime.timedelta(hours=self.targetObsLength,\
               minutes=1)

    def getTileBeam(self):
        """
        Compute the midpoint between the two pointings for the tile beam.
        Note that midpoint on the sky for large angular separation is
        ill-defined. In our case, it is almost always within ~7 degrees and
        so this function should be fine. For more details, see
        https://github.com/astropy/astropy/issues/5766
        """
        tempRA = (self.coordPoint1.ra.degree + self.coordPoint2.ra.degree)/2.
        tempDec = (self.coordPoint2.dec.degree + \
                   self.coordPoint2.dec.degree)/2.
        return SkyCoord(tempRA, tempDec, unit=u.deg)

    def findCalibrator(self, time):
        """
        For a given datetime, return a list of calibrators that are above
        the minimum elevation limit.
        """
        # Create the telescope object
        # The following values were taken from otool.py which is part of the
        # LOFAR source visibility calculator.
        lofar = Observer()
        lofar.lon = '6.869882'
        lofar.lat = '52.915129'
        lofar.elevation = 15.*u.m
        lofar.date = time
        
        # Create the target object
        target = FixedBody()
        target._epoch = '2000'
        target._ra = self.coordPoint1.ra.radian
        target._dec = self.coordPoint1.dec.radian
        target.compute(lofar)
        targetElevation = float(target.alt)*180./np.pi

        # Create the calibrator object
        calibrator = FixedBody()
        calibrator._epoch = '2000'
        calName = []
        distance = []
        for item in self.validCals:
            myCoord = getCalPointing(item)
            calibrator._ra = myCoord.split(';')[0]
            calibrator._dec = myCoord.split(';')[1]
            calibrator.compute(lofar)
            tempElevation = float(calibrator.alt)*180./np.pi
            if tempElevation > self.elevation:
                calName.append(item)
                distance.append(np.absolute(tempElevation-targetElevation))
        return calName[np.argmin(distance)]

    def distanceToSun(self):
        """
        Find the distance between the Sun and the target pointings
        """
        lofar = Observer()
        lofar.lon = '6.869882'
        lofar.lat = '52.915129'
        lofar.elevation = 15.*u.m
        lofar.date = self.startTime
        
        # Create Sun object
        sun = Sun()
        sun.compute(lofar)
        
        # Create the target object
        target = FixedBody()
        target._epoch = '2000'
        target._ra = self.coordPoint1.ra.radian
        target._dec = self.coordPoint1.dec.radian
        target.compute(lofar)
        print 'INFO: Sun is {:0.2f} degrees away from {}'.format(\
              float(separation(target, sun))*180./np.pi, self.namePoint1)
        target._ra = self.coordPoint2.ra.radian
        target._dec = self.coordPoint2.dec.radian
        target.compute(lofar)
        print 'INFO: Sun is {:0.2f} degrees away from {}'.format(\
              float(separation(target, sun))*180./np.pi, self.namePoint2)
        
def getCalPointing(calName):
    """
    Returns coordinates of standard flux density calibrators.
    """
    return {
        '3C295':'14:11:20.5;52:12:10',
        '3C196':'08:13:36.0;48:13:03',
        '3C48' :'01:37:41.3;33:09:35',
        '3C147':'05:42:36.1;49:51:07',
        '3C380':'18:29:31.8;48:44:46',
        '3C286':'13:31:08.3;30:30:33',
        'CTD93':'16:09:13.3;26:41:29',
    }[calName]

if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option('-p', '--project', help='Name of the project '+\
                   '[no default]', default='')
    opt.add_option('-m', '--main_name', help='Main folder name '+\
                   '[no default]', default='')
    opt.add_option('-d', '--date', help='Observation time in '+\
                   'yyyy-mm-dd-hh-mm-ss format [no default]', default='')
    opt.add_option('-t', '--time', help='Length of the target observation '+\
                   'in hours [default: 8 hours]', default='8')
    opt.add_option('-e', '--elevation', help='Minimum source elevation '+\
                   '[default: 20 degrees]', default='20')
    opt.add_option('-a', '--avg', help='Comma-separated freq and time '+\
                   'averaging factors [default=4,1]', default='4,1')
    opt.add_option('-x', '--point1', help='First beam info as '+\
                   '<name>,<ra>,<dec> [no default]', default='')
    opt.add_option('-y', '--point2', help="Second beam info as "+\
                   '<name>,<ra>,<dec> [no default]', default='')
    opt.add_option('-r', '--demix', help="Comma-separated source list "+\
                   "to demix (valid options: CasA, CygA, TauA, VirA) "+\
                   "[no default]", default='')
    opt.add_option('-o', '--output', help='Output filename [default='+\
                   ' output.txt', default='output.txt')
    options, args = opt.parse_args()

    # Extract user info
    pointing = PointingInfo(options)

    # Validate user input
    pointing.validateInput()
    
    # Open the output file
    outFile = open(options.output, 'w')

    # Write the header section
    pointing.makeHeader(outFile)

    # Write first calibrator block
    startTime = pointing.startTime
    try:
        calName = pointing.findCalibrator(startTime)
    except:
        raise IOError('A suitable flux calibrator could not be found.')
    print 'INFO: Using {} as flux calibrator'.format(calName)
    startTime = pointing.writeCalibrator(startTime, calName, outFile)

    # Generate target block
    startTime = pointing.writeTarget(startTime, outFile)

    # Write second calibrator block
    try:
        calName = pointing.findCalibrator(startTime)
    except:
        raise IOError('A suitable flux calibrator could not be found.')
    print 'INFO: Using {} as flux calibrator'.format(calName)
    startTime = pointing.writeCalibrator(startTime, calName, outFile)

    # Close the file
    outFile.close()
