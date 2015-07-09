#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Main loop for ActSim """

import sys
sys.path.append("tools/")
import numpy as np
import scipy.sparse as ssp

import time

from argParse import ArgParser
#~ from graphClass import GraphClass
from activitySimulator import Simulator
from xmlTools import strToBool, xmlToDict



#
#---
# Init modules
#--------------------

parser = ArgParser(description="ActSim: neural network activity simulator",usage='%(prog)s [options]')



#
#---
# Main loop
#--------------------

if __name__ == "__main__":
	
	#------------#
	# Parse args #
	#------------#
	
	args = parser.parseArgs()

	# get the xml trees

	dicTypes = {"float": float, "int": int, "bool": strToBool, "string": str}
	xmlSim = parser.xmlRoot.find("simulParam")
	dicSim = xmlToDict(xmlSim, dicTypes)
	
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
	
	#----------------------#
	# Create the simulator #
	#----------------------#

	actSimulator = Simulator(connectMat, dicSim)
	actSimulator.setParam()
	start = time.time()
	actSimulator.start()
	print(time.time() - start)
