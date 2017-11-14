#!/usr/bin/env python
"""
genSurveyTxt.py

Script to automatically generate observation setup (text) files for the
Tier-1 survey that can then be converted into an XML file.

Version 0.1 written 13/11/2017 by Sarrvesh S. Sridhar
"""
import optparse
import datetime
from astropy.coordinates import SkyCoord
import astropy.units as u

def validateInput(options):
    """
    Validate user input for
    - valid project and main folder names
    - pointing info
    - observing date
    - calibrators
    - valid sources to demix
    """
    if options.project == '':
        raise IOError('You must specify a valid project name.')
    if len(options.project) != 7:
        raise IOError('Specified project name is invalid.')
    if len(options.main_name) > 20:
        raise IOError('main_name cannot be more than 20 characters long.')
    if options.point1.count(',') != 2:
        raise IOError('Pointing info for first beam is invalid.')
    if options.point2.count(',') != 2:
        raise IOError('Pointing info for first beam is invalid.')
    if options.date == '':
        raise IOError('Invalid date specified.')
    if options.calib == '':
        raise IOError('Calibrators must be specified.')
    if options.avg != '4,1':
        print 'INFO: You have chosen a different averaging than the '+\
              'survey. Only the target will be averaged to the '+\
              'specified setup.'
    calList = options.calib.split(',')
    if len(calList) != 2:
        raise IOError('You must specify two bookend calibrators.')
    validCals = ['3C295', '3C196', '3C48', '3C147', '3C380', '3C286', \
                 'CTD93']
    for item in calList:
        if item not in validCals:
            raise IOError('{} is not a calibrator'.format(item))
    if options.demix != '':
        aTeamSrc = options.demix.split(',')
        validATeam = ['CasA', 'CygA', 'TauA', 'VirA']
        if len(aTeamSrc) > 2:
            raise IOError('Cannot demix more than two sources')
        for item in aTeamSrc:
            if item not in validATeam:
                raise IOError('Invalid A-team source specified.')

def makeHeader(projectName, mainFolderName, outFile):
    """
    Write the header section to the output text file
    """
    outFile.write('projectName={}\n'.format(projectName))
    outFile.write('mainFolderName={}\n'.format(mainFolderName))
    outFile.write('mainFolderDescription=Preprocessing:HBA Dual Inner,'+\
                  ' 110-190MHz, 8bits, 48MHz@144MHz, 1s, 64ch/sb\n\n')

def writeCalibrator(dateStr, calibName, avgStr, startTime, \
                    commonStr, outFile):
    """
    Write the calibrator section
    """
    outFile.write('BLOCK\n\n')
    outFile.write('packageName={}\n'.format(calibName))
    outFile.write('startTimeUTC={}\n'.format(startTime.isoformat(' ')))
    outFile.write('targetDuration_s=600\n')
    outFile.write(commonStr+'\n')
    outFile.write('targetBeams=\n')
    outFile.write('{};{};;;;;T;1800\n'.format(getCalPointing(calibName),\
                  calibName))
    outFile.write('Demix=4;1;64;10;;;F\n')
    outFile.write('\n')

    # Return the start time for the next block
    return startTime + datetime.timedelta(minutes=11)

def writeTarget(point1, point2, avg, aTeamSources, startTime, obsLength, outFile):
    """
    Write the target block.
    """
    outFile.write('BLOCK\n\n')
    outFile.write('packageName={}-{}\n'.format(point1.split(',')[0],
                                               point2.split(',')[0]))
    outFile.write('startTimeUTC={}\n'.format(startTime.isoformat(' ')))
    outFile.write('targetDuration_s={}\n'.format(int(obsLength*3600.)))
    outFile.write(commonStr+'\n')
    outFile.write('targetBeams=\n')
    # Compute the tile beam reference
    point1Coord = SkyCoord('{} {}'.format(point1.split(',')[1], \
                           point1.split(',')[2]), \
                           unit=(u.hourangle, u.deg))
    point2Coord = SkyCoord('{} {}'.format(point2.split(',')[1], \
                           point2.split(',')[2]), \
                           unit=(u.hourangle, u.deg))
    refCoord = getTileBeam(point1Coord, point2Coord)
    # Write the tile beam
    outFile.write('{};REF;256;1;;;F;31200\n'\
                  .format(refCoord.to_string(style='hmsdms', sep=':')\
                  .replace(' ', ';')))
    # Write the user pointing
    if aTeamSources == '':
        demix = ''
    else:
        demix = '[{}]'.format(aTeamSources)
        demix.replace(',', '')
    outFile.write('{};{};;;;;T;31200\n'\
                  .format(point1Coord.to_string(style='hmsdms', sep=':')\
                  .replace(' ', ';'), point1.split(',')[0]))
    outFile.write('Demix={};64;10;;{};F\n'.format(avg.replace(',', ';'), \
                  demix))
    # Write the tier-1 pointing
    outFile.write('{};{};;;;;T;31200\n'\
                  .format(point2Coord.to_string(style='hmsdms', sep=':')\
                  .replace(' ', ';'), point2.split(',')[0]))
    outFile.write('Demix=4;1;64;10;;;F\n')
    outFile.write('\n')
    # Return the start time for the next block
    return startTime + datetime.timedelta(hours=obsLength, minutes=1)

def getTileBeam(point1Coord, point2Coord):
    """
    Compute the midpoint between the two pointings for the tile beam.
    Note that midpoint on the sky for large angular separation is
    ill-defined. In our case, it is almost always within ~7 degrees and so
    this function should be fine. For more details, see
    https://github.com/astropy/astropy/issues/5766
    """
    tempRA = (point1Coord.ra.degree + point2Coord.ra.degree)/2.
    tempDec = (point1Coord.dec.degree + point2Coord.dec.degree)/2.
    return SkyCoord(tempRA, tempDec, unit=u.deg)

def getCalPointing(calName):
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
    opt.add_option('-a', '--avg', help='Comma-separated freq and time '+\
                   'averaging factors [default=4,1]', default='4,1')
    opt.add_option('-x', '--point1', help='First beam info as '+\
                   '<name>,<ra>,<dec> [no default]', default='')
    opt.add_option('-y', '--point2', help="Second beam info as "+\
                   '<name>,<ra>,<dec> [no default]', default='')
    opt.add_option('-c', '--calib', help="Comma-separated list of "+\
                   "calibrators [default=3C295,3C196]", default="3C295,"+\
                   "3C196")
    opt.add_option('-r', '--demix', help="Comma-separated source list "+\
                   "to demix (valid options: CasA, CygA, TauA, VirA) "+\
                   "[no default]", default='')
    opt.add_option('-o', '--output', help='Output filename [default='+\
                   ' output.txt', default='output.txt')
    options, args = opt.parse_args()

    # Define all parameters that are common to both cal and target blocks
    commonStr = "split_targets=F\ncalibration=none\n"\
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

    # Valid user input
    validateInput(options)

    # Extract user info
    calibs = options.calib.split(',')

    # Make the start time object
    dy, dm, ds, th, tm, ts = options.date.split('-')
    startTime = datetime.datetime(int(dy), int(dm), int(ds), \
                                  int(th), int(tm), int(ts))

    # Open the output file
    outFile = open(options.output, 'w')

    # Write the header section
    makeHeader(options.project, options.main_name, outFile)

    # Write first calibrator block
    startTime = writeCalibrator(options.date, calibs[0], options.avg, \
                                startTime, commonStr, outFile)

    # Generate target block
    startTime = writeTarget(options.point1, options.point2, options.avg, \
                            options.demix, startTime, \
                            float(options.time), outFile)

    # Write second calibrator block
    startTime = writeCalibrator(options.date, calibs[1], options.avg, \
                                startTime, commonStr, outFile)
    
    # Close the file
    outFile.close()
