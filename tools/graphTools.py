# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp
from copy import deepcopy

from graph_tool import *
from graph_tool.generation import geometric_graph
from graph_tool.stats import *
from graph_tool.util import *
from graph_tool.centrality import betweenness



#
#---
# Graph generators
#---------------------

def genGraphER(dicProperties):
	# on initialise le graphe
	graphERW = Graph()
	nNodes = 0
	nEdges = 0
	rDens = 0.0
	if "Nodes" in dicProperties.keys():
		nNodes = dicProperties["Nodes"]
		graphERW.add_vertex(nNodes)
		if "Edges" in dicProperties.keys():
			nEdges = dicProperties["Edges"]
			rDens = nEdges / float(nNodes**2)
			dicProperties["Density"] = rDens
		else:
			rDens = dicProperties["Density"]
			nEdges = int(np.floor(rDens*nNodes**2))
			dicProperties["Edges"] = nEdges
	else:
		nEdges = dicProperties["Edges"]
		rDens = dicProperties["Density"]
		nNodes = int(np.floor(np.sqrt(nEdges/rDens)))
		graphERW.add_vertex(nNodes)
		dicProperties["Nodes"] = nNodes
	# on génère les
	lstEdges = np.random.randint(0,nNodes,(nEdges,2))
	graphERW.add_edge_list(lstEdges)
	# on supprime les loops et doublons et on maj nEdges
	remove_self_loops(graphERW)
	remove_parallel_edges(graphERW)
	graphERW.reindex_edges()
	nNodes = graphERW.num_vertices()
	nEdges = graphERW.num_edges()
	rDens = nEdges / float(nNodes**2)
	# generate types
	rFracInhib = dicProperties["FracInhib"]
	lstTypesGen = np.random.uniform(0,1,nEdges)
	lstTypeLimit = np.full(nEdges,rFracInhib)
	lstIsExcitatory = np.greater(lstTypesGen,lstTypeLimit)
	nExc = np.count_nonzero(lstIsExcitatory)
	lstTypes = 2.0*lstIsExcitatory-1.0
	epropWeights = graphERW.new_edge_property("double",lstTypes) # excitatory (True) or inhibitory (False)
	graphERW.edge_properties["weight"] = epropWeights
	# and weights
	if dicProperties["Weighted"]:
		lstWeights = dicGenWeights[dicProperties["Distribution"]](graphERW,dicProperties,nEdges,nExc) # generate the weights
		graphERW.edge_properties["weight"].a = np.multiply(lstWeights,lstTypes)
	return graphERW

def genGraphFS(dicProperties):
	graphFS = Graph()
	# on définit la fraction des arcs à utiliser la réciprocité
	f = dicProperties["Reciprocity"]
	rFracRecip =  f/(2.0-f)
	# on définit toutes les grandeurs de base
	rInDeg = np.abs(dicProperties["InDeg"])
	rOutDeg = np.abs(dicProperties["OutDeg"])
	nNodes = 0
	nEdges = 0
	rDens = 0.0
	if "Nodes" in dicProperties.keys():
		nNodes = dicProperties["Nodes"]
		graphFS.add_vertex(nNodes)
		if "Edges" in dicProperties.keys():
			nEdges = dicProperties["Edges"]
			rDens = nEdges / float(nNodes**2)
			dicProperties["Density"] = rDens
		else:
			rDens = dicProperties["Density"]
			nEdges = int(np.floor(rDens*nNodes**2))
			dicProperties["Edges"] = nEdges
	else:
		nEdges = dicProperties["Edges"]
		rDens = dicProperties["Density"]
		nNodes = int(np.floor(np.sqrt(nEdges/rDens)))
		graphFS.add_vertex(nNodes)
		dicProperties["Nodes"] = nNodes
	# on définit le nombre d'arcs à créer
	nArcs = int(np.floor(rDens*np.square(nNodes))/(1+rFracRecip))
	# on définit les paramètres fonctions de probabilité associées F(x) = A x^{-tau}
	Ai = 1.3*nArcs*(rInDeg-1)/(nNodes)
	Ao = 1.3*nArcs*(rOutDeg-1)/(nNodes)
	# on définit les moyennes des distributions de pareto 2 = lomax
	rMi = 1/(rInDeg-2.)
	rMo = 1/(rOutDeg-2.)
	# on définit les trois listes contenant les degrés sortant/entrant/bidirectionnels associés aux noeuds i in range(nNodes)
	lstInDeg = np.random.pareto(rInDeg,nNodes)+1
	lstOutDeg = np.random.pareto(rOutDeg,nNodes)+1
	lstInDeg = np.floor(np.multiply(Ai/np.mean(lstInDeg), lstInDeg)).astype(int)
	lstOutDeg = np.floor(np.multiply(Ao/np.mean(lstOutDeg), lstOutDeg)).astype(int)
	# on génère les stubs qui vont être nécessaires et on les compte
	nInStubs = int(np.sum(lstInDeg))
	nOutStubs = int(np.sum(lstOutDeg))
	lstInStubs = np.zeros(np.sum(lstInDeg))
	lstOutStubs = np.zeros(np.sum(lstOutDeg))
	nStartIn = 0
	nStartOut = 0
	for vert in range(nNodes):
		nInDegVert = lstInDeg[vert]
		nOutDegVert = lstOutDeg[vert]
		for j in range(np.max([nInDegVert,nOutDegVert])):
			if j < nInDegVert:
				lstInStubs[nStartIn+j] += vert
			if j < nOutDegVert:
				lstOutStubs[nStartOut+j] += vert
		nStartOut+=nOutDegVert
		nStartIn+=nInDegVert
	# on vérifie qu'on a à peu près le nombre voulu d'edges
	while (nInStubs+nOutStubs)*(1+rFracRecip)/(2.0*nArcs) < 0.95 :
		vert = np.random.randint(0,nNodes)
		nAddInStubs = int(np.floor(Ai/rMi*(np.random.pareto(rInDeg)+1)))
		lstInStubs = np.append(lstInStubs,np.repeat(vert,nAddInStubs)).astype(int)
		nInStubs+=nAddInStubs
		nAddOutStubs = int(np.floor(Ao/rMo*(np.random.pareto(rOutDeg)+1)))
		lstOutStubs = np.append(lstOutStubs,np.repeat(vert,nAddOutStubs)).astype(int)
		nOutStubs+=nAddOutStubs
	# on s'assure d'avoir le même nombre de in et out stubs
	if nInStubs < nOutStubs:
		np.random.shuffle(lstOutStubs)
		lstOutStubs.resize(nInStubs)
		nOutStubs = nInStubs
	elif nInStubs > nOutStubs:
		np.random.shuffle(lstInStubs)
		lstInStubs.resize(nOutStubs)
		nInStubs = nOutStubs
	# on crée le graphe, les noeuds et les stubs
	nRecip = int(np.floor(nInStubs*rFracRecip))
	nEdges = nInStubs + nRecip +1
	# les stubs réciproques
	np.random.shuffle(lstInStubs)
	np.random.shuffle(lstOutStubs)
	lstInRecip = lstInStubs[0:nRecip]
	lstOutRecip = lstOutStubs[0:nRecip]
	lstEdges = np.array([np.concatenate((lstOutStubs,lstInRecip)),np.concatenate((lstInStubs,lstOutRecip))]).astype(int)
	# add edges
	graphFS.add_edge_list(np.transpose(lstEdges))
	remove_self_loops(graphFS)
	remove_parallel_edges(graphFS)
	graphFS.reindex_edges()
	nNodes = graphFS.num_vertices()
	nEdges = graphFS.num_edges()
	rDens = nEdges / float(nNodes**2)
	# generate types
	rFracInhib = dicProperties["FracInhib"]
	lstTypesGen = np.random.uniform(0,1,nEdges)
	lstTypeLimit = np.full(nEdges,rFracInhib)
	lstIsExcitatory = np.greater(lstTypesGen,lstTypeLimit)
	nExc = np.count_nonzero(lstIsExcitatory)
	lstTypes = 2.0*lstIsExcitatory-1.0
	epropWeights = graphFS.new_edge_property("double",lstTypes) # excitatory (True) or inhibitory (False)
	graphFS.edge_properties["weight"] = epropWeights
	# and weights
	if dicProperties["Weighted"]:
		lstWeights = dicGenWeights[dicProperties["Distribution"]](graphFS,dicProperties,nEdges,nExc) # generate the weights
		graphFS.edge_properties["weight"].a = np.multiply(lstWeights,lstTypes)
	return graphFS

def genGraphEDR(dicProperties):
	# on définit toutes les grandeurs de base
	rRho2D = dicProperties["Rho"]
	rLambda = dicProperties["Lambda"]
	nNodes = 0
	nEdges = 0
	rDens = 0.0
	if "Nodes" in dicProperties.keys():
		nNodes = dicProperties["Nodes"]
		if "Edges" in dicProperties.keys():
			nEdges = dicProperties["Edges"]
			rDens = nEdges / float(nNodes**2)
			dicProperties["Density"] = rDens
		else:
			rDens = dicProperties["Density"]
			nEdges = int(np.floor(rDens*nNodes**2))
			dicProperties["Edges"] = nEdges
	else:
		nEdges = dicProperties["Edges"]
		rDens = dicProperties["Density"]
		nNodes = int(np.floor(np.sqrt(nEdges/rDens)))
		dicProperties["Nodes"] = nNodes
	rSideLength = np.sqrt(nNodes/rRho2D)
	# generate the positions of the neurons
	lstPos = np.array([np.random.uniform(0,rSideLength,nNodes),np.random.uniform(0,rSideLength,nNodes)])
	lstPos = np.transpose(lstPos)
	nNumDesiredEdges = int(float(rDens*nNodes**2))
	graphEDR,pos = geometric_graph(lstPos,0)
	graphEDR.set_directed(True)
	graphEDR.vertex_properties["pos"] = pos
	# test edges building on random neurons
	nEdgesTot = graphEDR.num_edges()
	while nEdgesTot < nNumDesiredEdges:
		nTests = int(np.ceil(nNumDesiredEdges-nEdgesTot))
		lstVertSrc = np.random.randint(0,nNodes,nTests)
		lstVertDest = np.random.randint(0,nNodes,nTests)
		lstPosSrc = lstPos[lstVertSrc]
		lstPosDest = lstPos[lstVertDest]
		lstDist = np.linalg.norm(lstPosDest-lstPosSrc,axis=1)
		lstDist = np.exp(np.divide(lstDist,-rLambda))
		lstRand = np.random.uniform(size=nTests)
		lstCreateEdge = np.greater(lstDist,lstRand)
		nEdges = np.sum(lstCreateEdge)
		lstEdges = np.array([lstVertSrc[lstCreateEdge>0],lstVertDest[lstCreateEdge>0]]).astype(int)
		graphEDR.add_edge_list(np.transpose(lstEdges))
		nEdgesTot += nEdges
	# make graph simple and connected
	remove_self_loops(graphEDR)
	remove_parallel_edges(graphEDR)
	graphEDR.reindex_edges()
	nNodes = graphEDR.num_vertices()
	nEdges = graphEDR.num_edges()
	rDens = nEdges / float(nNodes**2)
	# generate types
	rFracInhib = dicProperties["FracInhib"]
	lstTypesGen = np.random.uniform(0,1,nEdges)
	lstTypeLimit = np.full(nEdges,rFracInhib)
	lstIsExcitatory = np.greater(lstTypesGen,lstTypeLimit)
	nExc = np.count_nonzero(lstIsExcitatory)
	lstTypes = 2.0*lstIsExcitatory-1.0
	epropWeights = graphEDR.new_edge_property("double",lstTypes) # excitatory (True) or inhibitory (False)
	graphEDR.edge_properties["weight"] = epropWeights
	# and weights
	if dicProperties["Weighted"]:
		lstWeights = dicGenWeights[dicProperties["Distribution"]](graphEDR,dicProperties,nEdges,nExc) # generate the weights
		graphEDR.edge_properties["weight"].a = np.multiply(lstWeights,lstTypes)
	return graphEDR


#
#---
# Weights generators
#---------------------

def genWGauss(graph,dicProperties,nEdges,nExc):
	rMeanExc = dicProperties["MeanExc"]
	rMeanInhib = dicProperties["MeanInhib"]
	rVarExc = dicProperties["VarExc"]
	rVarInhib = dicProperties["VarInhib"]
	lstWeightsExc = np.random.normal(rMeanExc,rVarExc,nExc)
	lstWeightsInhib = np.random.normal(rMeanInhib, rVarInhib, nEdges-nExc)
	lstWeights = np.concatenate((np.absolute(lstWeightsExc), np.absolute(lstWeightsInhib)))
	return lstWeights

def genWLogNorm(graph,dicProperties,nEdges,nExc):
	rScaleExc = dicProperties["ScaleExc"]
	rLocationExc = dicProperties["LocationExc"]
	rScaleinHib = dicProperties["ScaleInhib"]
	rLocationInhib = dicProperties["LocationInhib"]
	lstWeightsExc = np.random.lognormal(rLocationExc,rScaleExc,nExc)
	lstWeightsInhib = np.random.lognormal(rLocationInhib,rScaleInhib,nEdges-nExc)
	lstWeights = np.concatenate((np.absolute(lstWeightsExc), np.absolute(lstWeightsInhib)))
	return lstWeights

def genWBetweenness(graph,dicProperties,nEdges,nExc):
	lstWeights = np.zeros(nEdges)
	rMin = dicProperties["Min"]
	rMax = dicProperties["Max"]
	vpropBetw,epropBetw = betweenness(graph)
	lstWeights = deepcopy(epropBetw.a)
	rMaxBetw = lstWeights.max()
	rMinBetw = lstWeights.min()
	lstWeights = np.multiply(lstWeights-rMinBetw,rMax/rMaxBetw) + rMin
	return lstWeights

def genWDegree(graph,dicProperties,nEdges,nExc):
	lstWeights = np.zeros(nEdges)
	return lstWeights

dicGenWeights = {"Gaussian": genWGauss,
						"Lognormal": genWLogNorm,
						"Betweenness": genWBetweenness,
						"Degree": genWDegree}
