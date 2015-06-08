#!/usr/bin/python
############################################################################
##
## For a given list of frequencies, the code displays the corresponding RMSF
##
## Syntax: getRMSF.py <freq file> <phi min> <del phi> <n phi>
##
############################################################################
import sys
from numpy import median, zeros, exp, absolute, amin, amax, sqrt, pi
from matplotlib.pyplot import plot, xlabel, ylabel, show, legend
c = 299792458. # [m/s]

# Get the command line input
if len(sys.argv) != 5:
	print 'Invalid command line input. Terminating execution!\n'
	print 'Usage: '+sys.argv[0]+' <freq file> <phi min> <del phi> <n phi>\n'
	sys.exit()
freqFile = sys.argv[1]
minPhi	 = float(sys.argv[2])
delPhi	 = float(sys.argv[3])
nPhi	 = int(sys.argv[4])

# Read the list of frequencies
f 		 	 = open(freqFile,'r')
freqList_str = f.readlines()
# Convert the read frequencies to wavelengths and compute \lambda^2
lam  = []
lam2 = []
for i in range(len(freqList_str)):
	lam.append( (c/float(freqList_str[i])) )
	lam2.append( (c/float(freqList_str[i]))**2 )
f.close()
del freqList_str

# Compute \lambda_0^2
lam2_0 = median(lam2)

# Get the normalization factor K
K = 0
for i in range(len(lam2)):
	K += 1

# Compute the numerator of R(\phi)
maxPhi		= minPhi + delPhi*(nPhi-1)
absR  		= []
realR 		= []
imagR 		= []
phiArray 	= []
phi 		= minPhi
while phi < maxPhi:
	phiArray.append(phi)
	tempR = 0 + 0j
	for i in range(len(lam2)):
		tempR += exp(-2*1j*phi*(lam2[i]-lam2_0))
	absR.append( absolute(tempR)/K )
	realR.append( tempR.real/K )
	imagR.append( tempR.imag/K )
	phi += delPhi

# Print stats
fwhm 	= 3.8 / (amax(lam2)-amin(lam2)) # from Schnitzeler et al (2008)
maxSize = pi/amin(lam2)
print '\nFor a top-hat weight function:\n'
print '\tFWHM: '+str(fwhm)+' rad/m2'
print '\tMax scale: '+str(maxSize)+' rad/m2 \n'

# Make plots
absVal = plot(phiArray,absR,'black',label='|R|')
realVal=plot(phiArray,realR,'r--',label='real(R)')
imagVal=plot(phiArray,imagR,'b--',label='imag(R)')
xlabel('Faraday depth [rad/m^2]')
ylabel('RMSF')
legend()
show()
