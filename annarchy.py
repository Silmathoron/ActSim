#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Testing ANNarchy """

from ANNarchy import *
#~ import matplotlib.pyplot as plt
import pylab as plt

from argParse import ArgParser
from graphClass import GraphClass
from xmlTools import strToBool, xmlToDict

setup(num_threads=5)
#~ dt = 0.5
#~ setup(dt=dt)

#
#---
# Init objects
#--------------------

#------------#
# Parse args #
#------------#

parser = ArgParser(description="ANNarchy: neural network activity simulator",usage='%(prog)s [options]')

args = parser.parseArgs()

# get the xml trees

dicTypes = {"float": float, "int": int, "bool": strToBool, "string": str}
xmlSim = parser.xmlRoot.find("simulParam")
xmlNet = parser.xmlRoot.find("netParam")
dicSim = xmlToDict(xmlSim, dicTypes)

#------------------#
# Create the graph #
#------------------#

dicGraph = xmlToDict(xmlNet,dicTypes)
graph = GraphClass(dicGraph)


#
#---
# Build ANNarchy network
#------------------------------

#~ pop = Population(geometry=1000, neuron=IF_curr_exp)
#~ pop.set({'tau_refrac': 2})
#~ pop.noise = 5
pop = Population(name='pop', geometry=1000, neuron=Izhikevich)
re = np.random.random(1000)
pop.noise = 2.1
pop.a = 0.02
pop.b = 0.2
pop.c = -65.0 + 15.0 * re**2
pop.d = 8.0 - 6.0 * re**2
pop.v = -65.0
pop.u = pop.v * pop.b

# get excitatory connections

epropType = graph.getGraph().new_edge_property("bool",graph.getGraph().edge_properties["weight"].a>0)
graph.getGraph().set_edge_filter(epropType)
matExc = graph.getAdjacency()

# get inhibitory connections

graph.getGraph().clear_filters()
epropType = graph.getGraph().new_edge_property("bool",graph.getGraph().edge_properties["weight"].a<0)
graph.getGraph().set_edge_filter(epropType)
matInhib = np.abs(graph.getAdjacency())

#--------------------#
# Connect population #
#--------------------#

projExc = Projection(
     pre = pop,
     post = pop,
     target = 'exc'
)

projInhib = Projection(
     pre = pop,
     post = pop,
     target = 'inh'
)

projExc.connect_from_sparse(matExc.tolil(), delays = 2.0)
projInhib.connect_from_sparse(matInhib.tolil(), delays = 2.0)

compile()

projExc.disable_learning()
projInhib.disable_learning()


#
#---
# Run the simulation
#------------------------------

if __name__ == "__main__":

	#----------#
	# Activity #
	#----------#
	
	m = Monitor(pop, ['v', 'spike'])
	rBinDuration = 4. # ms
	simulate(50000.0)

	#--------------------#
	# Avalanche analysis #
	#--------------------#
	
	## get the spike informations
	
	data = m.get('spike')
	spike_times, ranks = m.raster_plot(data)
	print(len(spike_times))
	arrArgsTimeSort = np.argsort(spike_times)
	spike_times = spike_times[arrArgsTimeSort]
	ranks = ranks[arrArgsTimeSort]
	idxLastSpike = len(spike_times)-1

	if idxLastSpike != -1:

		## group the avalanches
		
		lstAvalancheSizes = []
		lstAvalancheDurations = []
		idxAvalancheStart = -1
		rAvalancheStartTime = spike_times[0]
		for idx,time in enumerate(spike_times[1:]):
			if time-rAvalancheStartTime > rBinDuration and idx != idxLastSpike:
				lstAvalancheSizes.append(idx-idxAvalancheStart)
				lstAvalancheDurations.append(spike_times[idx]-rAvalancheStartTime + rBinDuration)
				idxAvalancheStart = idx
				rAvalancheStartTime = time
			elif idx == idxLastSpike:
				lstAvalancheSizes.append(idx-idxAvalancheStart)
				lstAvalancheDurations.append(time-rAvalancheStartTime)

		print("{}\n{}".format(lstAvalancheDurations[:10],lstAvalancheSizes[:10]))

		## histogram
		
		numBins = len(lstAvalancheDurations) / 2
		
		nMinSize = np.amin(lstAvalancheSizes)
		nMaxSize = np.amax(lstAvalancheSizes)
		arrBins = np.logspace(np.log10(nMinSize), np.log10(nMaxSize), numBins)
		arrCountsSizes, arrSizes = np.histogram(lstAvalancheSizes, arrBins)
		print(arrCountsSizes[:10], arrSizes[:10])

		rMinDuration = np.amin(lstAvalancheDurations)
		rMaxDuration = np.amax(lstAvalancheDurations)
		arrBins = np.logspace(np.log10(rMinDuration), np.log10(rMaxDuration), numBins)
		arrCountsDurations, arrDurations = np.histogram(lstAvalancheDurations, arrBins)

		#----------#
		# Plotting #
		#----------#

		## Durations and sizes

		figScaling = plt.figure()
		axSizeVsDuration = plt.subplot(2,2,1)
		axSizeVsDuration.loglog(lstAvalancheDurations, lstAvalancheSizes)

		axSizeHisto = plt.subplot(2,2,2)
		axSizeHisto.loglog(arrSizes[:-1], arrCountsSizes)
		
		axDurationHisto = plt.subplot(2,2,3)
		axDurationHisto.loglog(arrDurations[:-1], arrCountsDurations)

		## raster

		figRaster = plt.figure()
		axRaster1 = plt.subplot(2,1,1)
		axRaster1.plot(spike_times, ranks, 'b.', markersize=1.0)
		
		## Second plot: membrane potential of a single excitatory cell
		
		axRaster2 = plt.subplot(2,1,2)
		axRaster2.plot(m.get('v')[:, 15])
		plt.show()
