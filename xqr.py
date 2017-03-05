#XQR: XML Query
#Author: Jakub Svoboda
#Login: xsvobo0z
#Email: xsvobo0z@stud.fit.vutbr.cz
#Date: 4. March 2017

import argparse
import sys
import re
import os
from enum import Enum
from xml.dom import minidom

#define error codes
PARAMETER_ERROR=1
INPUT_ERROR=2
OUTPUT_ERROR=3

#define tokens
TOKEN_SELECT=1
TOKEN_ELEMENT=2
TOKEN_FROM=3
TOKEN_LIMIT=4
TOKEN_NUMBER=5
TOKEN_STRING=6
TOKEN_ROOT=7
TOKEN_WHERE=8
TOKEN_NOT=9
TOKEN_CONTAINS=10
TOKEN_EQUAL=11
TOKEN_GREATER=12
TOKEN_LESS=13
TOKEN_ATTRIBUTE=14
TOKEN_EOF=15

#class defining one token from query
class Token:	
	def __init__(self,type,value):
		self.type=type
		self.value=value			
	def getType(self):
		return self.type
	def getValue(self):
		return self.value	

#class defining the query		
class QueryText:
	def __init__(self,text):
		self.queryText=text
		
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

#copies the query from either the parameter or the source file into a string		
def getQuery(results):	
	if(results.qf):
		file=open(results.qf,'r')
		queryText=file.read()
		file.close
	else:
		queryText=results.query		
		
	text = QueryText(queryText)	
	text.queryText = re.sub("'\r\n'", r"' '", text.queryText)		#replace newlines
	return text
	
#lexical analyser of the query	
def getToken(text):
	tokenStr = str("")
	index=0
	for letter in text.queryText:
		#tokenStr+=str(letter)
		if(letter == ' ' or letter == "<" or letter == ">" or letter == "=" or letter == "\t"):
			if(len(tokenStr)==0):
				tokenStr+=str(letter)
			break
		index+=1
		tokenStr+=str(letter)
		
		
		
	print(tokenStr)	
	tokenStr=re.sub(r'^\s+',"",tokenStr)										#trim spaces from around the token
	tokenStr=re.sub(r'\s+$',"",tokenStr)
	text.queryText=re.sub(tokenStr, '', text.queryText,1)						#remove the token from query string
	text.queryText=re.sub(r'^\s+',"",text.queryText)							#trim spaces from around the rest of query string
	text.queryText=re.sub(r'\s+$',"",text.queryText)
	#01 SELECT 
	if(tokenStr == "SELECT"):	
		token = Token(TOKEN_SELECT,"SELECT")
	#03 FROM	
	elif(tokenStr == "FROM"):	
		token = Token(TOKEN_FROM,"FROM")
	#04 LIMIT	
	elif(tokenStr == "LIMIT"):	
		token = Token(TOKEN_LIMIT,"LIMIT")
	#07 ROOT
	elif(tokenStr == "ROOT"):	
		token = Token(TOKEN_ROOT,"ROOT")
	#08 WHERE
	elif(tokenStr == "WHERE"):	
		token = Token(TOKEN_WHERE,"WHERE")
	#09 NOT
	elif(tokenStr == "NOT"):	
		token = Token(TOKEN_NOT,"NOT")	
	#10 CONTAINS
	elif(tokenStr == "CONTAINS"):	
		token = Token(TOKEN_CONTAINS,"CONTAINS")	
	#11 EQUAL
	elif(tokenStr == "="):	
		token = Token(TOKEN_EQUAL,"EQUAL")
	#12 GREATER
	elif(tokenStr == ">"):	
		token = Token(TOKEN_GREATER,"GREATER")	
	#13 LESS
	elif(tokenStr == "<"):	
		token = Token(TOKEN_LESS,"LESS")
	#elif(tokenStr)	
	else:
		return None
	
	
	return token
	
#Analyzes the syntax of the query and executes
def parse(results):	
	inputFile = open(results.input,'r')			#open the xml file	 TODO safe open
	xml = minidom.parse(inputFile)
	inputFile.close()	
	text = getQuery(results)
	i=0
	while(i<12):		#get tokens one by one
		getToken(text)
		i+=1
		
	
	



	
				
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

