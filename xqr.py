#XQR: XML Query
#Author: Jakub Svoboda
#Login: xsvobo0z
#Email: xsvobo0z@stud.fit.vutbr.cz
#Date: 4. March 2017

import argparse
import sys
import re
import os
from xml.dom import minidom

PARAMETER_ERROR=1
INPUT_ERROR=2
OUTPUT_ERROR=3

#prints help when a --help parameter is found and ends the program
def printHelp(results):
	if(results.input or results.output or results.query or results.qf or results.n or results.root):
		sys.stderr.write("Help cannot be used with any other parameter.\n")
		exit(PARAMETER_ERROR)
	print("XQR: XML Query")
	print("Parameters:")
	print("	--help: to print out a manual")
	print("	--input=filename: to specify a input file")
	print("	--output=filename: sets the output file")
	print("	--query=dotaz: set a query specified by the language")
	print("	--qf=filename: query specified by the language, cannot be combined with --query")
	print("	--n: negates the XML header")
	print("	--root=element: name of the element that wrapps the results")

#controls whether or not the passed arguments are valid 
def checkParameters(results,unknown):
	if(results.help):							#help has been found
		printHelp(results)
	if(results.qf and results.query):			#--qf and --query combination
		sys.stderr.write("--qf cannot be used with --query\n")
		exit(PARAMETER_ERROR)
	if(unknown):								#unknown parameters
		sys.stderr.write("Unrecognised parameter.\n")
		exit(PARAMETER_ERROR)
	if(results.qf):								#controls valid --qf path
		if(not(os.path.exists(results.qf))):
			sys.stderr.write("--qf file not found:	%s\n" % results.qf)
			exit(INPUT_ERROR)						#TODO is error ok?
		if(not os.path.isfile(results.qf)):	
			sys.stderr.write("--qf file is not file:	%s\n" % results.qf)
			exit(INPUT_ERROR)						#TODO is error ok?
	if(results.qf == ""):
		sys.stderr.write("--qf empty value	%s\n" % results.qf)
		exit(PARAMETER_ERROR)						#TODO is error ok?
	
	if(not results.input):						#validates the --input file	
		sys.stderr.write("--input parameter not found\n");
		exit(INPUT_ERROR)
	else:										
		if(results.input):
			if(not os.path.exists):
				sys.stderr.write("--input file not found:	%s\n" % results.input)
				exit(INPUT_ERROR)					#TODO is error ok?
			if(not os.path.isfile(results.input)):	
				sys.stderr.write("--input file is not file:	%s\n" % results.input)
				exit(INPUT_ERROR)					#TODO is error ok?
				
	if(not results.output):						#Check whether or not the output parameter is ok
		sys.stderr.write("--output parameter not found\n");
		exit(PARAMETER_ERROR)						#TODO what error should this be?
		
#Analyzes the syntax of the query and executes
def parse(results):		
	Test_file = open(results.input,'r')
	xmldoc = minidom.parse(Test_file)
	Test_file.close()
	printNode(xmldoc.documentElement)
	
def printNode(node):
	print (node)
	for child in node.childNodes:
		printNode(child)

		
				
#MAIN:	
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--help', action='store_true',default=False, dest='help')
parser.add_argument('--input', action='store', dest='input')
parser.add_argument('--output', action='store', dest='output')
parser.add_argument('--query', action='store', dest='query')
parser.add_argument('--qf', action='store', dest="qf")
parser.add_argument('-n', action='store_true', default=False, dest='n')
parser.add_argument('--root', action='store', dest="root")
results, unknown = parser.parse_known_args()
checkParameters(results, unknown)
parse(results)

