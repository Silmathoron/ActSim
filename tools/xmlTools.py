#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" XML tools """

import xml.etree.ElementTree as xmlet
import numpy as np



#
#---
# Utils
#------------------------

## translate string to boolean

def strToBool(string):
	return True if (string == "True" or string == "true") else False


#
#---
# XML/dict conversions
#------------------------

## converting dictionary to XML

def dictToXml(dico, root = None):
	base = None
	if root is not None:
		base = root
	else:
		base = xmlet.Element("base")
	for key,value in dico.items():
		elt = xmlet.Element(key)
		if value.__class__ == dict:
			elt = dictToXml(value, elt)
		else:
			elt.text = str(value)
		base.append(elt)
	return base

## converting XML to dictionary

def xmlToDict(xmlElt, dicTypes):
	dicResult = {}
	for child in xmlElt:
		strType = child.tag
		strName = child.attrib["name"]
		if len(child):
			elt = child.find("start")
			if elt is not None:
				start = dicTypes[strType](child.find("start").text)
				stop = dicTypes[strType](child.find("stop").text)
				step = dicTypes[strType](child.find("step").text)
				dicResult[strName] = np.arange(start,stop,step)
			else:
				dicResult[strName] = xmlToDict(child, dicTypes)
		else:
			dicResult[strName] = dicTypes[strType](child.text)
	return dicResult
