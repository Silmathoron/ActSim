#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Dataprocessor for ActSim """

import numpy as np
import scipy.sparse as ssp
import matplotlib.pyplot as plt



#
#---
# Data processing class
#-------------------------

class DataProc:
	
	#-------------#
	# Constructor #
	#-------------#
	
	def __init__(self, dicParam):
		# simulation parameters
		self.dicParam = dicParam.copy()
		# statistics
		self.lstBurstSizes = []
		self.lstBurstDuration = []
		self.lstBurstIntervals = []

	
	#------------------#
	# Event processing #
	#------------------#
	
	def processEvent(self, nBurstSpikes, nBurstDuration, nInterval):
		self.lstBurstSizes.append(nBurstSpikes)
		self.lstBurstDuration.append(nBurstDuration)
		self.lstBurstIntervals.append(nInterval)

	
	#------------#
	# Statistics #
	#------------#

	def getHisto(self):
		numBursts = len(self.lstBurstDuration)
		numBins = int(numBursts/10)
		# Size (gen log separated bins)
		vecSizes = np.array(self.lstBurstSizes)
		vecBins = np.logspace(np.log10(max(vecSizes.min(),1)), np.log10(vecSizes.max()), numBins)
		vecSizeCount,vecSizeBin = np.histogram(vecSizes, vecBins)
		# Interval
		vecIntervals = np.array(self.lstBurstIntervals)
		vecBins = np.logspace(np.log10(max(vecIntervals.min(),1)), np.log10(vecIntervals.max()), numBins)
		vecIntervalCount,vecIntervalBin = np.histogram(vecIntervals, vecBins)
		# Duration
		vecDuration = np.array(self.lstBurstDuration)
		vecBins = np.logspace(np.log10(max(vecDuration.min(),1)), np.log10(vecDuration.max()), numBins)
		vecDurationCount,vecDurationBin = np.histogram(vecDuration, vecBins)
		#~ print(np.equal(vecDurationCount, vecSizeCount))

		#~ fig, axes = plt.subpolts(nrows=2, ncols=2)
		plt.subplot(2, 2, 1)
		plt.loglog(vecIntervalBin[:-1], vecIntervalCount, ls='None', marker='o', c='green', alpha=0.5)
		plt.xlabel('Interval between successive bursts')
		plt.ylabel('Counts')
		plt.subplot(2, 2, 2)
		plt.loglog(vecSizeBin[:-1], vecSizeCount, ls='None', marker='o', c='blue', alpha=0.5)
		plt.xlabel('Size of the burst')
		plt.ylabel('Counts')
		plt.subplot(2, 2, 3)
		plt.loglog(vecDurationBin[:-1], vecDurationCount, ls='None', marker='o', c='red', alpha=0.5)
		plt.xlabel('Duration of the burst')
		plt.ylabel('Counts')
		plt.tight_layout()
		
		plt.show()
	
	
		
