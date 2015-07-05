#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Main loop for ActSim """

import sys
sys.path.append("build/")
import numpy as np
import scipy.sparse as ssp

import time

from argParse import ArgParser
#~ from graphClass import GraphClass
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
	#~ graph = GraphClass(dicGraph)
	#~ nNodes = graph.getNodes()
	nNodes = 1000
	connectMat = ssp.rand(1000,1000,0.012,'csr')
	csrData = [nNodes, connectMat.indptr.tolist(), connectMat.indices.tolist(), connectMat.data.tolist()]
	
	#----------------------#
	# Create the simulator #
	#----------------------#

	actSimulator = libsimulator.Simulator(csrData, parser.xmlRoot)
	actSimulator.setParam()
	start = time.time()
	actSimulator.start()
	print(time.time() - start)
	#~ actSimulator = libsimulator.Simulator(csrData)
