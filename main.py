#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Main loop for ActSim """

import sys
sys.path.append("tools/")
import numpy as np
import scipy.sparse as ssp

import time

from argParse import ArgParser
from graphClass import GraphClass
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
	xmlNet = parser.xmlRoot.find("netParam")
	dicSim = xmlToDict(xmlSim, dicTypes)
	
	#------------------#
	# Create the graph #
	#------------------#
	
	dicGraph = xmlToDict(xmlNet,dicTypes)
	graph = GraphClass(dicGraph)
	connectMat = graph.getAdjacency()
	
	#----------------------#
	# Create the simulator #
	#----------------------#

	actSimulator = Simulator(connectMat, dicSim)
	actSimulator.setParam()
	start = time.time()
	actSimulator.start()
	print(time.time() - start)
