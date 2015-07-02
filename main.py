#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Main loop for ActSim """

import sys
sys.path.append("build/")
import numpy as np

from argParse import ArgParser
from graphClass import GraphClass
import libsimulator



#
#---
# Init modules
#--------------------

parser = ArgParser(description="AlgoGen: graph generator for reservoir computing",usage='%(prog)s [options]')



#
#---
# Main loop
#--------------------

if __name__ == "__main__":
	None
	#------------#
	# Parse args #
	#------------#

	args = parser.parseArgs()

	# get the xml trees
	
	#------------------#
	# Create the graph #
	#------------------#
	
	dicGraph = {"Type": "Erdos-Renyi",
					"Nodes": 1000,
					"Density": 0.01,
					"FracInhib": 0.5,
					"Weighted": True,
					"Distribution": "Gaussian",
					"Reciprocity": 0.2,
					"InDeg": 2.5,
					"OutDeg": 2.5,
					"MeanExc": 1,
					"MeanInhib": 1,
					"VarExc": 0.2,
					"VarInhib": 0.2}
	graph = GraphClass(dicGraph)
	nNodes = graph.getNodes()
	connectMat = graph.getAdjacency()
	csrData = [nNodes, connectMat.indptr, connectMat.indices, connectMat.data]
	
	#----------------------#
	# Create the simulator #
	#----------------------#

	actSimulator = libsimulator.Simulator(csrData, parser.xmlRoot)
	actSimulator.start()
	#~ actSimulator = libsimulator.Simulator(csrData)
