#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" ArgumentParser for AlgoGen """

import sys
sys.path.append("tools/")
from xmlTools import strToBool, xmlToDict

import argparse
import shutil
import xml.etree.ElementTree as xmlet


#
#---
# Class inheriting from argparse
#----------------------------------

class ArgParser(argparse.ArgumentParser):

	#------------#
	# Initialize #
	#------------#
	def __init__(self, description, usage):
		""" init that inherits from argparse """
		super(ArgParser, self).__init__(description,usage)
		self.args = None
		saveGroup = self.add_mutually_exclusive_group()
		# adding the arguments
		self.add_argument("-f", "--fromfile", action="store", default="data/param.xml",
							help="Load parameters from XML file.")
		self.add_argument("-c","--cleanup",action="store_true", default=0,
							help="Remove all previous files")
		self.add_argument("-q","--quiet", action="store_true", default=0,
							help="Do not show progress informations")
		saveGroup.add_argument("-ns", "--no-save", action="store_true", default=0,
							help="Do not save individuals")
		saveGroup.add_argument("-o", "--output", action="store", default="results/activity",
							help="Output file for the activity")
		saveGroup.add_argument("-s","--stats", action="store", default="results/stats",
							help="Output file for the statistics")
		# xml parser info
		self.dicType = {"float": float,
						"int": int,
						"str": str,
						"bool": strToBool}
		self.xmlRoot = None

	#-------#
	# Parse #
	#-------#
	def parseArgs(self):
		""" call the argparse command, then apply args """
		self.args = self.parse_args()
		self._getParameters()

	#--------------------#
	# Process parameters #
	#--------------------#

	## get XML parameters
	
	def _getParameters(self):
		""" process the xml file """
		try:
			tree = xmlet.parse(self.args.fromfile)
			self.xmlRoot = tree.getroot()
			#~ self.simulParam = root.find("simulParam")
			#~ self.neuronParam = root.find("neuronParam")
			#~ self.netParam = root.find("netParam")
		except Exception as e:
			print(e)
			raise IOError("There might be a problem with the required\
XML file containing the parameters")
		print(xmlToDict(self.xmlRoot[1],self.dicType))

	
