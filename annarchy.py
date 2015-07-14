#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Testing ANNarchy """

from ANNarchy import *
#~ import matplotlib.pyplot as plt
import pylab as plt

from argParse import ArgParser
from graphClass import GraphClass
from xmlTools import strToBool, xmlToDict

setup(num_threads=4)

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
#~ pop.set({'tau_refrac': 5})
#~ pop.noise = 2.0
pop = Population(name='Exc', geometry=1000, neuron=Izhikevich)
re = np.random.random(1000)
pop.noise = 2.5
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

projExc.connect_from_sparse(matExc.tolil(), delays = 3.0)
projInhib.connect_from_sparse(matInhib.tolil(), delays = 3.0)

compile()


#
#---
# Run the simulation
#------------------------------

# monitoring

m = Monitor(pop, ['v', 'spike'])

# simulate

simulate(10000.0)


# plot
data = m.get('spike')
spike_times, ranks = m.raster_plot(data)
ax = plt.subplot(2,1,1)
ax.plot(spike_times, ranks, 'b.', markersize=1.0)
# Second plot: membrane potential of a single excitatory cell
ax = plt.subplot(2,1,2)
ax.plot(m.get('v')[:, 15])
plt.show()
