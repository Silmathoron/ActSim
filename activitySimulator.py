#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Main loop for ActSim """

import sys
sys.path.append("tools/")
import numpy as np
import scipy.sparse as ssp



#
#---
# Simulator class
#---------------------

class Simulator:
	
	#-------------#
	# Constructor #
	#-------------#
	
	def __init__(self, csrMat, dicParam, dataProc):
		# main objects
		self.matConnect = csrMat
		self.bRunning = False
		self.nNeurons = csrMat.shape[0]
		# simulation, neurons and network parameters
		self.dicParam = dicParam
		# avalanches container
		self.bBursting = False
		self.dataProc = dataProc
		#~ self.matAvalanches = ssp.lil_matrix((self.nNeurons, self.nTotStep), dtype=np.int16)
	
	
	#------------#
	# Initialize #
	#------------#
	
	def setParam(self):
		for key, value in self.dicParam.items():
			if key == "Threshold":
				self.rThreshold = value
			elif key == "Leak":
				self.rLeak = value
			elif key == "Refrac":
				self.rRefrac = value
			elif key == "SimulTime":
				self.rSimulTime = value
			elif key == "TimeStep":
				self.rTimeStep = value
			elif key == "NoiseStdDev":
				self.rNoiseStdDev = value
			elif key == "AvgPot":
				self.rAvgPot = value
			elif key == "RestPot":
				self.rRestPotential = value
			elif key == "SpikeDelay":
				self.rSpikeDelay = value
			elif key == "SpikePotential":
				self.rSpikePotential = value
			else:
				raise TypeError("Wrong XML parameters")
		self.nTotStep = int(np.floor(self.rSimulTime / self.rTimeStep))
		self.nRefrac = int(np.floor(self.rRefrac / self.rTimeStep))
		self.nSpikeDelay = int(np.floor(self.rSpikeDelay / self.rTimeStep))
		self.rSqrtStep = np.sqrt(self.rTimeStep)
	
	
	#------------#
	# Simulation #
	#------------#
	
	## running
	
	def start(self):
		if not self.bRunning:
			self.bRunning = True
			print("Starting run")
			self.runSimulation()
	
	def runSimulation(self):
		# init vectors
		vecPotential, vecRestPotential, vecActive = self.initPotential()
		vecThreshold = np.repeat(self.rThreshold, self.nNeurons)
		vecRefractory = np.zeros(self.nNeurons, dtype=np.int8)
		vecExcitable = np.repeat(True, self.nNeurons).astype(bool)
		vecSpike = np.repeat(self.rSpikePotential,self.nNeurons)
		vecSpikeTarget = np.array([], dtype=np.int32)
		vecSpikeDelay = np.array([], dtype=np.int32)
		vecIndices = self.matConnect.indices
		vecIndptr = self.matConnect.indptr
		print("all initiated")
		# run
		nBurstSpikes = 0
		nInterval = 0
		nBurstDuration = 0
		for i in range(self.nTotStep):
			vecPotential += ( (vecRestPotential-vecPotential) * self.rTimeStep + self.rSqrtStep * np.random.normal(0.,self.rNoiseStdDev, self.nNeurons)) / self.rLeak 
			numNNZ = len(vecSpikeTarget)
			# decrement spike arrival time
			#~ idxLastTarget = 0
			#~ if numNNZ:
				#~ vecSpikeDelay -= 1
				#~ # get neurons that received the only spike traveling on their axon
				#~ idxZeroDelay = np.where(vecSpikeDelay == 0)[0]
				#~ idxReceived = vecSpikeTarget[idxZeroDelay]
				#~ if idxZeroDelay.size:
					#~ vecSpikeDelay = vecSpikeDelay[idxZeroDelay[-1]:]
					#~ vecSpikeTarget = vecSpikeTarget[idxZeroDelay[-1]:]
					#~ # upgrade the neurons that receive their spikes and are not refractory
					#~ vecPotential[idxReceived] += np.multiply(vecExcitable[idxReceived], vecSpike[idxReceived])
			#~ print(vecRefractory[0:10])
			# get new spiking neurons and update avalanche container
			vecBoolActive = np.multiply(vecExcitable, np.greater(vecPotential,vecThreshold))
			#~ print(np.sum(vecBoolActive))
			vecRefractory[vecBoolActive] = self.nRefrac
			vecActive = np.where(vecBoolActive)[0]
			#~ print(np.sum(vecRefractory>0))
			if not vecActive.any():
				if self.bBursting:
					self.dataProc.processEvent(nBurstSpikes, nBurstDuration, nInterval)
					nInterval = 0
				nInterval += 1
				nBurstDuration = 0
				nBurstSpikes = 0
				self.bBursting = False
			else:
				self.bBursting = True
				# add spikes
				nBurstDuration += 1
				nBurstSpikes += np.sum(vecBoolActive)
				#~ vecNewTargets = np.array([], dtype=np.int32)
				#~ for idx in vecActive:
					#~ vecRow = vecIndices[vecIndptr[idx]:vecIndptr[idx+1]]
					#~ if vecRow.size:
						#~ vecNewTargets = np.concatenate((vecNewTargets, vecRow))
				#~ vecSpikeTarget = np.concatenate((vecSpikeTarget, vecNewTargets))
				#~ vecSpikeDelay = np.concatenate((vecSpikeDelay, np.repeat(self.nSpikeDelay, len(vecNewTargets))))
			# decrement refractory period
			vecReset = vecRefractory.astype(bool)
			vecRefractory[vecRefractory>0] -= 1
			vecExcitable = ~vecRefractory.astype(bool)
			vecReset *= vecExcitable
			vecPotential[vecReset] = self.rRestPotential
		if self.bBursting:
			self.dataProc.processEvent(nBurstSpikes, nBurstDuration, nInterval)
		
	## initialize
	
	def initPotential(self):
		rGaussScale = max(np.abs(self.rAvgPot - self.rRestPotential),5) / 2.
		vecPotential = np.random.normal(loc=self.rAvgPot, scale=rGaussScale, size=self.nNeurons)
		vecRestPotential = np.random.normal(loc=self.rRestPotential, scale=rGaussScale, size=self.nNeurons)
		vecActive = np.floor(np.random.uniform(0.,0.3,self.nNeurons)).astype(bool)
		return vecPotential, vecRestPotential, vecActive
	

	#---------------#
	# Communication #
	#---------------#
		
	def get_results(self):
		return None
	
	def getTotSteps(self):
		return self.nTotStep
