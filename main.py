#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Main loop for ActSim """

from argParse import ArgParser
import numpy as np



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

	#------------#
	# Parse args #
	#------------#

	parser.parseArgs()

	# get the xml trees
