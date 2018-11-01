import matplotlib.pyplot as plt
import numpy as np

def blockAverage(datastream, showPlot=True, maxBlockSize=0, sectionSize=100,
				 dataFileName=None, plotFileName=None, varName='x',
				 returnSimple=False):

	"""This program computes the block average of a potentially correlated timeseries "x", and
	provides error bounds for the estimated mean <x>.
	As input provide a vector or timeseries "x", and the largest block size.

	Check out writeup in the following blog posts for more:
	http://sachinashanbhag.blogspot.com/2013/08/block-averaging-estimating-uncertainty_14.html
	http://sachinashanbhag.blogspot.com/2013/08/block-averaging-estimating-uncertainty.html

	Arguments:
	datastream - a 1D array containing the dependent variable
	showPlot - boolean specifying whether the block means and block variances
	should be plotted
	maxBlockSize - an integer specifying the maximum size of a block
	sectionSize - an integer specifying the number of blocks in each section
	used to calculate the variance of the original distribution
	dataFileName - a string specifying the file name of the mean and standard
	deviation output, not including the extension
	plotFileName - a string specifying the file name of the plot output, not
	including the extension, which is set to png
	varName - a string specifying the name of the variable for plotting,
	data file output, and plot output
	returnSimple - if True then a string containing the formatted mean and
	standard deviation are returned

	Returns:
	The block number, the variances corresponding to the block numbers, the
	means correpsonding to the block number.
	Unless returnSimple == True then a string containing the formatted mean and
	standard deviation are returned
	"""

	Nobs         = len(datastream)           # total number of observations in datastream
	minBlockSize = 1                        # min: 1 observation/block

	if maxBlockSize == 0:
		maxBlockSize = int(Nobs/16)        # max: 4 blocs (otherwise can't calc variance)

	NumBlocks = maxBlockSize - minBlockSize   # total number of block sizes

	blockMean = np.zeros(NumBlocks)               # mean (expect to be "nearly" constant)
	blockVar  = np.zeros(NumBlocks)               # variance associated with each blockSize
	blockCtr  = 0

				#
				#  blockSize is # observations/block
				#  run them through all the possibilities
				#

	for blockSize in range(minBlockSize, maxBlockSize):

		Nblock    = int(Nobs/blockSize)               # total number of such blocks in datastream
		obsProp   = np.zeros(Nblock)                  # container for parcelling block

		# Loop to chop datastream into blocks
		# and take average
		for i in range(1,Nblock+1):

			ibeg = (i-1) * blockSize
			iend =  ibeg + blockSize
			obsProp[i-1] = np.mean(datastream[ibeg:iend])

		blockMean[blockCtr] = np.mean(obsProp)
		blockVar[blockCtr]  = np.var(obsProp)/(Nblock - 1)
		blockCtr += 1

	v = np.arange(minBlockSize,maxBlockSize)

	std = calculateStd(v, blockVar, sectionSize=sectionSize)

	if dataFileName:

		with open(dataFileName + '.val', 'w') as file:
			file.write(formatOutput(np.mean(blockMean), std, varName))

	if showPlot or plotFileName:
		plt.subplot(2,1,1)
		plt.plot(v, np.sqrt(blockVar),'ro-',lw=2)
		plt.xlabel('block size')
		plt.ylabel('std')

		plt.subplot(2,1,2)
		plt.errorbar(v, blockMean, np.sqrt(blockVar))
		plt.ylabel('<' + varName + '>')
		plt.xlabel('block size')

		print(formatOutput(np.mean(blockMean), std, varName))

		plt.tight_layout()

		if plotFileName:
			plt.savefig(plotFileName + '.png')

		if showPlot:
			plt.show()

		plt.close()

	if returnSimple:
		return formatOutput(np.mean(blockMean), std, varName)
	return v, blockVar, blockMean


def formatOutput(mean, std, varName='x'):

	"""
	Returns correct output string for mean and error (standard deviation)
	"""

	return '<' + varName + '> = {0:f} +/- {1:f}\n'.format(mean, std)


def calculateStd(v, blockVar, sectionSize=20):

	"""
	Calculates the standard deviation from the blockVar by fitting sections of
	blockVar with a flat line

	The variances for the section which has the smallest residual for fitting a
	flat line are averaged and assumed to be the closest to the true variance of
	the original distribution.  Follows naming convention of blockAverage
	function.

	Arguments:
	v - an array of integers specifying the block number
	blockVar - an array of floats with the variances corresponding to the block
	numbers in v
	sectionSize - the number of blocks in each section which is fit with a
	flat line

	Returns:
	Standard deviation of section with smallest variance from a flat line (i.e.
	y = constant)
	"""

	variances = []
	residuals = []
	for i in range(0, len(v) - sectionSize):
		var, res = np.polyfit(v[i:i+sectionSize],
							  blockVar[i:i+sectionSize],
							  0,
							  cov=True)
		variances.append(var)
		residuals.append(np.trace(res))

	# Get the variance at the cell where the residual is the smallest (square
	# rooted for std)
	std = np.array(variances)[residuals == np.min(residuals)] ** 0.5

	return np.float(std)
