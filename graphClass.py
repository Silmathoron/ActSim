#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" GraphClass: graph generation and management """

import sys
sys.path.append("tools/")
from graphTools import  genGraphER, genGraphFS, genGraphEDR

import numpy as np
from graph_tool import *
from graph_tool.spectral import adjacency
from copy import deepcopy



#
#---
# GraphClass
#------------------------

class GraphClass:

	#------------#
	# Initialize #
	#------------#
	
	def __init__(self, dicProp={"Name": "Graph", "Type": "None", "Weighted": False}, graph=None):
		# on récupère les propriétés
		self.dicProperties = deepcopy(dicProp)
		self.dicGenGraphType = {"Erdos-Renyi": genGraphER,
						"Free-scale": genGraphFS,
						"EDR": genGraphEDR}
		# on génère un graphe
		if graph is not None:
			self.graph = gtGraph.copy()
			self.updateProp()
		elif dicProp["Type"] == "None":
			self.graph = Graph()
		else:
			self.graph = self.dicGenGraphType[dicProp["Type"]](self.dicProperties)
			self.setName()
			self.updateProp()

	#------------------#
	# Graph management #
	#------------------#

	## copying
	
	def copyGraph(self,gtGraphToCopy):
		self.graph = gtGraphToCopy.copy()

	def deepcopyGraph(self,gtGraphToCopy):
		self.graph = Graph(gtGraphToCopy)
		self.updateProp()
	
	## set graph to existing graph-tool graph

	def setGraph(self,gtGraphToCopy):
		self.graph = gtGraphToCopy
		self.updateProp()

	## excitatory and exhibitory subgraphs
	
	def genInhibSubgraph(self):
		graph = self.graph.copy()
		epropType = graph.new_edge_property("bool",-graph.edge_properties["type"].a+1)
		graph.set_edge_filter(epropType)
		inhibGraph = GraphClass()
		inhibGraph.setGraph(Graph(graph,prune=True))
		inhibGraph.setProp("Weighted", True)
		return inhibGraph

	def genExcSubgraph(self):
		graph = self.graph.copy()
		epropType = graph.new_edge_property("bool",graph.edge_properties["type"].a+1)
		graph.set_edge_filter(epropType)
		excGraph = GraphClass()
		excGraph.setGraph(Graph(graph,prune=True))
		excGraph.setProp("Weighted", True)
		return excGraph

	#---------------#
	# Set functions #
	#---------------#

	def setName(self, strName = ""):
		if strName:
			self.dicProperties["Name"] = strName
		else:
			string = self.dicProperties["Type"]
			for key,value in self.dicProperties.items():
				if (key != "Type") and (key != "Weighted") and (value.__class__ != dict):
					string += key[0] + str(value)
			self.dicProperties["Name"] = string

	def setDicProp(self,dicProp):
		for strKey,value in dicProp.items():
			self.dicProperties[strKey] = value

	def setProp(self, strProp, valProp):
		self.dicProperties[strProp] = valProp

	#---------------#
	# Get functions #
	#---------------#

	def getName(self):
		return self.dicProperties["Name"]

	def getGraph(self):
		return self.graph

	def getNodes(self):
		return self.dicProperties["Nodes"]

	def getNumEdges(self):
		return self.dicProperties["Edges"]

	def getProp(self):
		return self.xmlProp

	def isWeighted(self):
		return self.dicProperties["Weighted"]
	
	def getAdjacency(self):
		if self.isWeighted():
			return adjacency(self.graph, self.graph.edge_properties["weight"])
		else:
			return adjacency(self.graph)

	#----------#
	# Updating #
	#----------#
	
	def updateProp(self, dicProp=None, lstProp=None):
		# basic properties
		nNodes = self.graph.num_vertices()
		self.dicProperties["Nodes"] = nNodes
		nEdges = self.graph.num_edges()
		self.dicProperties["Edges"] = nEdges
		self.dicProperties["Density"] = nEdges / float(np.square(nNodes))
		# special properties
		if dicProp == None and lstProp == None:
			None
		elif lstProp == None:
			for prop in dicProp.keys():
				self.dicProperties[prop] = dicProp[prop]
		else:
			if "FracInhib" in lstProp:
				self.dicProperties["FracInhib"] = getNumInhib(self.graph)/float(nEdges)

	#-----------#
	# Destroyer #
	#-----------#

	def __del__(self):
		print('Graph died')
