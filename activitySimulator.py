#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Main loop for ActSim """

import sys
sys.path.append("tools/")
import numpy as np
import scipy.sparse as ssp

from xmlTools import xmlToDict



#
#---
# Simulator class
#---------------------

class Simulator:
	
	#-------------#
	# Constructor #
	#-------------#
	
	def __init__(self, csrMat, xmlRoot);
		# main objects
		self.matConnect = csrMat
		self.bRunning = False
		self.nNeurons = csrMat.shape[0]
		self.dicTypes = {}
		# simulation, neurons and network parameters
		dicParam = xmlToDict(xmlRoot)
		self.setParam(dicParam)
		# avalanches container
		self.matAvalanches = ssp.lil_matrix((self.nNeurons, self.nTotStep), dtype=np.int16)
	
	
	#------------#
	# Initialize #
	#------------#
	
	def setParam(self, dicParam):
		for key, value in dicParam.items():
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
				self.rRestPot = value
			elif key == "SpikeDelay":
				self.nSpikeDelay = value
			elif key == "SpikePotential":
				self.rSpikePotential = value
			else:
				raise TypeError("Wrong XML parameters")
		self.nTotStep = int(np.floor(self.rSimulTime / self.rTimeStep))
		self.nRefrac = int(np.floor(self.rRefrac / self.rTimeStep))
		self.rSqrtStep = np.sqrt(self.rTimeStep)
	
	
	#------------#
	# Simulation #
	#------------#
	
	## running
	
	def start(self);
		if not self.bRunning:
			self.bRunning = True
			print("Starting run")
			self.runSimulation()
	
	def runSimulation(self):
		# init vectors
		vecPotential, vecRestPotential, vecActive = self.initPotential()
		vecThreshold = np.repeat(self.rThreshold, self.nNeurons)
		vecRefractory = np.zeros(self.nNeurons, dtype=bool)
		vecSpike = np.repeat(self.rSpikePotential,self.nNeurons)
		# init matrix (lil matrix automatically gets rid of the zeros)
		matSpikes = ssp.lil_matrix((self.nNeurons, self.nNeurons), dtype=np.int8)
		matSpikesTMP = ssp.lil_matrix((self.nNeurons, self.nNeurons), dtype=list)
		matDecrement = ssp.lil_matrix((self.nNeurons, self.nNeurons), dtype=np.int8)
		matAvalanche = np.array([ [] for _ in range(self.nNeurons) ])
		# run
		for i in range(self.nTotStep):
			vecPotential += ( (vecRestPotential-vecPotential) / self.rTimeStep + self.rSqrtStep * np.random.normal(0.,self.rNoiseStdDev, self.nNeurons) ) / self.rLeak
			numNNZ = matSpikes.nnz
			# decrement spike arrival time
			if numNNZ:
				idxNNZ = matSpikes.nonzero()
				matSpikesTMP[idxNNZ] = matSpikes[idxNNZ]
				matDecrement[idxNNZ] = 1
				matSpikes -= matDecrement
				# get neurons that received the only spike traveling on their axon
				idxNNZ_post = matSpikes.nonzero()
				matSpikesTMP[idxNNZ_post] = 0
				idxReceived = matSpikesTMP.nonzero()[0]
				# upgrade the neurons that receive their spikes
				vecPotential[idxReceived] += np.multiply(~vecRefractory[idxReceived], vecSpike[idxReceived])
				# get new spiking neurons and update avalanche container
				vecBoolActive = np.greater(vecPotential,vecThreshold)
				vecActive = np.where()[0]
				if not vecActive.any():
					""" SEND THE AVALANCHE VECTOR TO THE DATA PROCESSOR """
					matAvalanche = np.array([ [] for _ in range(self.nNeurons) ])
				else:
					matAvalanche[vecBoolActive>0] += [i]
				# add spikes
				matSpike[:,vecActive] = self.nSpikeDelay * self.matConnect[:,vecActive].astype(bool)
				# decrement refractory period
				vecReset = vecRefractory.astype(bool)
				vecRefractory[vecRefractory>0] -= 1
				vecReset *= ~vecRefractory.astype(bool)
				vecPotential[vecReset] = self.rRestPotential
				# reset tool matrices
				matDecrement[idxNNZ] = 0
				matSpikesTMP[idxNNZ] = 0
		
	## initialize
	
	def initPotential(self):
		rGaussScale = np.abs(self.rAvgPot - self.rRestPot) / 2.
		vecPotential = np.random.normal(loc=self.rAvgPot, scale=rGaussScale, size=self.nNeurons)
		vecRestPotential = np.random.normal(loc=self.rRestPot, scale=rGaussScale, size=self.nNeurons)
		vecActive = np.floor(np.random.uniform(0.,0.3,self.nNeurons)).astype(bool)
		return vecPotential, vecRestPotential, vecActive
	

	#---------------#
	# Communication #
	#---------------#
		
	def get_results(self):
		return None
