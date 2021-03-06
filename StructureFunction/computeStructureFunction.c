#include<stdio.h>
#include<string.h>
#include<stdlib.h>
#include<math.h>
#include<limits.h>

#define SUCCESS 0
#define FAILURE 1
#define nINPUTS 7

#define round(x) ((x)>=0?(long)((x)+0.5):(long)((x)-0.5))
#define TO_DEG 180/M_PI
#define TO_RAD M_PI/180

double angDistDeg(double th1, double ph1, double th2, double ph2);

/**********************************************************************
 * Computes the angular distance in deg for a given set of (ra, dec) 
 * coordinates in degrees.
 **********************************************************************/
double angDistDeg(double th1, double ph1, double th2, double ph2)
{
    double ra1rad, ra2rad, dec1rad, dec2rad;
    double x, y, z, rad;
    
    ra1rad = th1*TO_RAD;
    ra2rad = th2*TO_RAD;
    dec1rad= ph1*TO_RAD;
    dec2rad= ph2*TO_RAD;
    
    x=cos(ra1rad)*cos(dec1rad)*cos(ra2rad)*cos(dec2rad);
    y=sin(ra1rad)*cos(dec1rad)*sin(ra2rad)*cos(dec2rad);
    z=sin(dec1rad)*sin(dec2rad);
    
    if(x+y+z >= 1)  { rad = 0.0; }
    else            { rad = acos(x+y+z); }
    
    return rad*TO_DEG;
}

int main(int argc, char *argv[])  {
    /* Initialize command line arguments */
    char *pixelListFileName = argv[1];
    long   nPixels  = atoi(argv[2]);
    double binStart = atof(argv[3]);
    int    nBins    = atoi(argv[4]);
    double binSize  = atof(argv[5]);
    char *plotValsFileName  = argv[6];
    double binEnd   = binStart + nBins*binSize;
    /* Declare all other variables */
    FILE *ptr;
    double *RA, *Dec, *RM, *eRM;
    double *rmSqDiff, *angDist, *angLogDist, *varSum;
    unsigned long long int nCorrelations, index;
    int i, j;
    double minRMDiff, maxRMDiff, minAngDist, maxAngDist;
    double minVarSum, maxVarSum;
    double *histBinsForRM, *histBinsForeRM, *histXAxis;
    int *histBinsCount;
    
    /* Check if command line arguments are valid */
    if(argc != nINPUTS) {
        printf("\nERROR: Invalid list of command line arguments.");
        printf("\nERROR: Terminating execution!");
        exit(FAILURE);
    }
    
    /* Allocate memory to store ra, dec, rm and eRM values */
    RA  = calloc(nPixels, sizeof(RA));
    Dec = calloc(nPixels, sizeof(Dec));
    RM  = calloc(nPixels, sizeof(RM));
    eRM = calloc(nPixels, sizeof(eRM));
    
    /* Open the specified file and read the input values */
    printf("INFO: Reading %ld lines from file %s", nPixels, pixelListFileName);
    ptr = fopen(pixelListFileName, "r");
    if(ptr == NULL) {
        printf("\nERROR: Unable to read the pixel list from disk.\n");
        exit(FAILURE);
    }
    for(i=0; i< nPixels; i++)
        fscanf(ptr, "%lf %lf %lf %lf", &RA[i], &Dec[i], &RM[i], &eRM[i]); 
    fclose(ptr);
    
    /* From the list of pixels, form all possible correlations */
    nCorrelations = nPixels*(nPixels-1)/2;
    printf("\nINFO: Forming %lld correlations.", nCorrelations);
    /* Allocate memory to store the correlations */
    rmSqDiff   = calloc(nCorrelations, sizeof(rmSqDiff));
    varSum     = calloc(nCorrelations, sizeof(varSum));
    angDist    = calloc(nCorrelations, sizeof(angDist));
    angLogDist = calloc(nCorrelations, sizeof(angLogDist));
    index = 0;
    //ptr = fopen("checkDistance.txt", "w");
    for(i=0; i<nPixels; i++)     {
        for(j=i+1; j<nPixels; j++) {            
            /* Compute the squared difference of RM */
           	rmSqDiff[index] = pow(RM[i] - RM[j], 2);
            /* Compute the squared sum of the noise */
           	varSum[index] = pow(eRM[i],2) + pow(eRM[j],2);
            /* Find the distance between the two pixels in this correlation */
            angDist[index] = angDistDeg(RA[i], Dec[i], RA[j], Dec[j]);
            angLogDist[index] = log10(angDist[index]);
           
            /* Keep track of the min and max of both rmSqDiff and angLogDiff */
            if(index == 0)  {
                minRMDiff = rmSqDiff[index];
                maxRMDiff = rmSqDiff[index];
                minAngDist= angDist[index];
                maxAngDist= angDist[index];
                minVarSum = varSum[index]; 
                maxVarSum = varSum[index];
            }
            else {
                if(minRMDiff > rmSqDiff[index]) { minRMDiff = rmSqDiff[index]; }
                if(maxRMDiff < rmSqDiff[index]) { maxRMDiff = rmSqDiff[index]; }
                if(minAngDist > angDist[index]) { minAngDist = angDist[index]; }
                if(maxAngDist < angDist[index]) { maxAngDist = angDist[index]; }
                if(minVarSum > varSum[index])   { minVarSum = varSum[index];   }
                if(maxVarSum < varSum[index])   { maxVarSum = varSum[index];   }
            }            
            if(index%(nCorrelations/10) == 0)
            	printf("\nINFO: Processing index %lld/%lld", index, nCorrelations);
            index+=1;
        }
    }
    printf("\nINFO: RM Difference Min: %lf and Max: %lf", minRMDiff, maxRMDiff);
    printf("\nINFO: Angular distance Min: %lf and Max: %lf", minAngDist, maxAngDist);
    printf("\nINFO: Angular distance in log. Min: %lf and Max: %lf", log10(minAngDist), log10(maxAngDist));
    printf("\nINFO: Sum of error in RM Min: %lf and Max: %lf", minVarSum, maxVarSum);
    
    /* Allocate memory for histogram bins */
    printf("\nINFO: Binning data with");
    printf("\n\tStart value: %lf", binStart);
    printf("\n\tBin Size: %lf", binSize);
    printf("\n\tNo. of bins: %d", nBins);
    histBinsForRM = calloc(nBins, sizeof(histBinsForRM));
    histBinsForeRM= calloc(nBins, sizeof(histBinsForeRM));
    histBinsCount = calloc(nBins, sizeof(histBinsCount));
    histXAxis     = calloc(nBins, sizeof(histBinsCount));
    /* Compute the x-axis values for a given hist setup */
    for(i=0; i<nBins; i++) { 
        histXAxis[i] = i*binSize + binStart - binSize/2; 
    }

    /* Do histogram binning */
    index = 0;
    for(i=0; i<nCorrelations; i++)	{
    	/* Filter out distances that don't fall within the */
    	/* specified bin range. Also filter out nan and inf*/
    	if(angLogDist[i]<binSize && angLogDist[i]>binEnd)  { continue; }
    	if(isinf(angLogDist[i]) || isnan(angLogDist[i]))   { continue; }
    	if(isinf(rmSqDiff[i])   || isnan(rmSqDiff[i]))     { continue; }
    	if(isinf(varSum[i])     || isnan(rmSqDiff[i]))     { continue; }
    	/* If the values are valid, bin them */
    	/* j takes values from 0 to nBins    */
    	j = round(fabs((binStart - angLogDist[i])/binSize));
    	histBinsForRM [j] += rmSqDiff[i];
    	histBinsForeRM[j] += varSum[i];
    	histBinsCount [j] += 1;
    	index+=1;
    }
    printf("\nINFO: %lld/%lld valid values were used for binning.", index, nCorrelations);
    
    /* Compute the averages in each bin */
    for(i=0; i<nBins; i++)	{
    	if(histBinsCount[i] == 0)	{
    		histBinsForRM [i] = NAN;
    		histBinsForeRM[i] = NAN;
    	}
    	histBinsForRM [i] /= histBinsCount[i];
    	histBinsForeRM[i] /= histBinsCount[i];
    }
    
    /* Write structure function to disk */
    /* Format: <X Axis value> <binned RM> <binned eRM> <# per bin> */
    printf("\nINFO: Writing structure function to %s.", plotValsFileName);
    ptr = fopen(plotValsFileName, "w");
    for(i=0; i<nBins; i++)
    	fprintf(ptr, "%lf %lf %lf %d\n", histXAxis[i], histBinsForRM[i], histBinsForeRM[i], histBinsCount[i]);
    fclose(ptr);
    printf("\n");   
    return SUCCESS;
}
