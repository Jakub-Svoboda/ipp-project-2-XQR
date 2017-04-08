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
import xml.etree.ElementTree as ET

#define error codes
PARAMETER_ERROR=1
INPUT_ERROR=2
OUTPUT_ERROR=3
FORMAT_ERROR=4

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
TOKEN_ORDER=16
TOKEN_BY=17
TOKEN_ASC=18
TOKEN_DESC=19

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

#prints the error description and exits with code
def printError(code,description):
	sys.stderr.write(description)
	exit(code)		
	
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
	exit(0)

#controls whether or not the passed arguments are valid 
def checkParameters(results,unknown):
	if(results.help):							#help has been found
		printHelp(results)
	if(results.qf and results.query):			#--qf and --query combination
		sys.stderr.write("--qf cannot be used with --query\n")
		exit(PARAMETER_ERROR)
	if(not results.qf and not results.query):	#no query
		sys.stderr.write("No query given.\n")
		exit(PARAMETER_ERROR)	
	if(unknown):								#unknown parameters
		sys.stderr.write("Unrecognised parameter.\n")
		exit(PARAMETER_ERROR)
	if(results.qf):								#controls valid --qf path
		if(not(os.path.exists(results.qf))):
			sys.stderr.write("--qf file not found:	%s\n" % results.qf)
			exit(80)						
		if(not os.path.isfile(results.qf)):	
			sys.stderr.write("--qf file is not file:	%s\n" % results.qf)
			exit(80)						
	if(results.qf == ""):
		sys.stderr.write("--qf empty value	%s\n" % results.qf)
		exit(PARAMETER_ERROR)						
	
	if(not results.input):						#validates the --input file	
		sys.stderr.write("--input parameter not found\n");
		exit(INPUT_ERROR)
	else:										
		if(results.input):
			if(not os.path.exists):
				sys.stderr.write("--input file not found:	%s\n" % results.input)
				exit(INPUT_ERROR)					
			if(not os.path.isfile(results.input)):	
				sys.stderr.write("--input file is not file:	%s\n" % results.input)
				exit(INPUT_ERROR)					
				
	if(not results.output):						#Check whether or not the output parameter is ok
		sys.stderr.write("--output parameter not found\n");
		exit(PARAMETER_ERROR)					

#copies the query from either the parameter or the source file into a string		
def getQuery(results):	
	if(results.qf):
		try:
			file=open(results.qf,'r')			
			queryText=file.read()
			file.close()
		except:
			printError(80,"Query file read error.\n")
	else:
		queryText=results.query		
		
	text = QueryText(queryText)	
	text.queryText = re.sub("'\r\n'", r"' '", text.queryText)		#replace newlines
	return text
	
#lexical analyser of the query	
def getToken(text):
	tokenStr = str("")
	for letter in text.queryText:
		if(letter == ' ' or letter == "<" or letter == ">" or letter == "=" or letter == "\t" or letter == "\"" or letter == "\'"):	#if letter is delimiter			
			if(len(tokenStr)==0):			
				if(letter == "\"" or letter =="\'"):
					try:
						tokenStr+= re.search(r'"(.*?)"',text.queryText).group(0)
						break
					except:
						printError(80,"Syntax error.\n")
				tokenStr+=str(letter)				
			break
		tokenStr+=str(letter)

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
	#16 ORDER
	elif(tokenStr == "ORDER"):	
		token = Token(TOKEN_ORDER,"ORDER")	
	#17 BY
	elif(tokenStr == "BY"):	
		token = Token(TOKEN_BY,"BY")		
	#18 ASC
	elif(tokenStr == "ASC"):	
		token = Token(TOKEN_ASC,"ASC")	
	#19 DESC
	elif(tokenStr == "DESC"):	
		token = Token(TOKEN_DESC,"DESC")	
	#06 STRING	
	elif((tokenStr.startswith('"') and tokenStr.endswith('"')) or (tokenStr.startswith('\'') and tokenStr.endswith('\''))):			tokenStr = tokenStr[1:-1]
		token = Token(TOKEN_STRING, tokenStr)
	#05 NUMBER	
	elif(tokenStr.isdigit() or ((tokenStr[1:].isdigit() and tokenStr[0]=="+") or (tokenStr[1:].isdigit() and tokenStr[0]=="-"))):	
		token = Token(TOKEN_NUMBER,tokenStr)
	#02 ELEMENT
	elif((not tokenStr.isspace()) and len(tokenStr) != 0):
		token = Token(TOKEN_ELEMENT,tokenStr)
	else:
		token = Token(TOKEN_EOF, "EOF")
	
	
	return token

#searches for all sublemenets recursively, that match the element	
def searchSubElemsRec(root,element,result):
	if(root.tag == element and root not in result):
		result.append(root)
	for item in list(root):
		if(item.tag == element):
			result.append(item)
		searchSubElemsRec(item, element, result)
	return result
	
#searches for all sublemenets recursively, even if they dont match	
def searchSubElemsRecAll(root,result):
	if(root not in result):
		result.append(root)
	for item in list(root):
		result.append(item)
		searchSubElemsRecAll(item,result)
	return result	

#orders the elements by given element value or attrubute in ascending or descending order:
def orderResult(result,order,orderElement,orderAttribute):
	elementValue=[]
	fullPass=False
	rev=True
	if(order.getType()==TOKEN_ASC):
		rev=False	
		
	if(orderElement!="" and orderAttribute!=""):	#element.attribute
		try:
			result.sort(key = lambda x: x.find(orderElement).get(orderAttribute), reverse=rev)
		except:
			printError(4,"Sorting error.\n")
	elif(orderElement!="" and orderAttribute==""):	#element
		try:
			result.sort(key = lambda x: x.find(orderElement).text, reverse=rev)	
		except:
			printError(4,"Sorting error.\n")
	elif(orderElement=="" and orderAttribute!=""):	#.attribute	
		try:
			result.sort(key = lambda x: x.get(orderAttribute), reverse=rev)
		except:
			printError(4,"Sorting error.\n")
	
	for index, item in enumerate(result):
		item.attrib["order"] = str(index+1)	
	return result
	
#filter the elements based on the ocndition from WHERE clause\n
def filterWhere(nots, result, whereElement, whereAttribute, operator, literal):
	elementValue=[]
	toint=True
	if(literal.getType() == TOKEN_NUMBER and operator.getType() == TOKEN_CONTAINS):		
		printError(80,"Syntax error: CONTAINS operator cannot be used with a number.\n")
	if(literal.getType()== TOKEN_NUMBER):			#numeric comparison
		threshold = int(literal.getValue())	
	else:											#alphanumeric comparison
		threshold = literal.getValue()
		toint=False	
	for idx, item in enumerate(result):	
		if(whereElement!="" and whereAttribute!=""):	#element.attribute
			elementValue=[]
			elementValue=searchSubElemsRec(item,whereElement,elementValue)
			if(elementValue == []):													#the element for comparison not found in given element, element is removed
				result[idx]=None
			else:																	#element contains the searched element
				if(whereAttribute in elementValue[0].attrib):							#element also contains the searched attribute					
					#if(len(elementValue)>idx):									
					if(toint and operator.getType()!=TOKEN_CONTAINS):		
						try:
							comparison=float(elementValue[0].get(whereAttribute))					
						except:
							result[idx]=None
							continue
					else:
						comparison=elementValue[0].get(whereAttribute)	
					if(operator.getType() == TOKEN_LESS):				#<	
						if(comparison>=threshold and (nots%2 == 0)): 								
							result[idx]=None
						elif(comparison<threshold and (nots%2 == 1)):
							result[idx]=None
					elif(operator.getType() == TOKEN_GREATER):			#>
						if(comparison<=threshold and (nots%2 == 0)): 
							result[idx]=None
						elif(comparison>threshold and (nots%2 == 1)):
							result[idx]=None
					elif(operator.getType() == TOKEN_EQUAL):			#=
						if(comparison!=threshold and (nots%2 == 0)): 
							result[idx]=None
						elif(comparison==threshold and (nots%2 == 1)):
							result[idx]=None	
					elif(operator.getType() == TOKEN_CONTAINS):			#CONTAINS 
						try:
							if((not (threshold in comparison)) and (nots%2 == 0)):				
								result[idx]=None
							elif((threshold in comparison) and (nots%2 == 1)):	
								result[idx]=None
						except:
							pass		
				else:																#element found, but does not have the attribute
					result[idx]=None
		elif(whereElement!="" and whereAttribute==""):	#element
			elementValue=searchSubElemsRec(item,whereElement,elementValue)
			if(elementValue == []):													#the element for comparison not found in given element, element is removed
				result[idx]=None
			else:																	#element contains the value for comparison
				if(len(elementValue)>idx):				#<what is that?
					if(toint and operator.getType()!=TOKEN_CONTAINS):				
						try:
							comparison=float(elementValue[idx].text)				
						except:
							result[idx]=None
							continue											
					else:
						comparison=elementValue[idx].text
					if(operator.getType() == TOKEN_LESS):				#<	
						if(comparison>=threshold and (nots%2 == 0)): 
							result[idx]=None
						elif(comparison<threshold and (nots%2 == 1)):
							result[idx]=None
					elif(operator.getType() == TOKEN_GREATER):			#>
						if(comparison<=threshold and (nots%2 == 0)): 
							result[idx]=None
						elif(comparison>threshold and (nots%2 == 1)):
							result[idx]=None		
					elif(operator.getType() == TOKEN_EQUAL):			#=
						if(comparison!=threshold and (nots%2 == 0)): 
							result[idx]=None
						elif(comparison==threshold and (nots%2 == 1)):
							result[idx]=None		
					elif(operator.getType() == TOKEN_CONTAINS):			#CONTAINS
						try:
							if((not (threshold in comparison)) and (nots%2 == 0)):				
								result[idx]=None
							elif((threshold in comparison) and (nots%2 == 1)):	
								result[idx]=None
						except:
							pass
		elif(whereElement=="" and whereAttribute!=""):	#.attribute
			#elementValue=searchSubElemsRecAll(item,elementValue)
			if(whereAttribute in item.attrib):							#element also contains the searched attribute
				if(toint and operator.getType()!=TOKEN_CONTAINS):			
					try:
						comparison=float(item.get(whereAttribute))					
					except:
						result[idx]=None
						continue	
				else:
					comparison=item.get(whereAttribute)
				if(operator.getType() == TOKEN_LESS):				#<	
					if(comparison>=threshold and (nots%2 == 0)): 
						result[idx]=None
					elif(comparison<threshold and (nots%2 == 1)):
						result[idx]=None
				elif(operator.getType() == TOKEN_GREATER):			#>
					if(comparison<=threshold and (nots%2 == 0)): 
						result[idx]=None
					elif(comparison>threshold and (nots%2 == 1)):
						result[idx]=None		
				elif(operator.getType() == TOKEN_EQUAL):			#=
					if(comparison!=threshold and (nots%2 == 0)): 
						result[idx]=None
					elif(comparison==threshold and (nots%2 == 1)):
						result[idx]=None	
				elif(operator.getType() == TOKEN_CONTAINS):			#CONTAINS 
					try:
						if((not (threshold in comparison)) and (nots%2 == 0)):				
							result[idx]=None
						elif((threshold in comparison) and (nots%2 == 1)):	
							result[idx]=None
					except:
						pass
			else:
				result[idx]=None
			
	result=[item for item in result if item is not None]	#Removes the None elements from result
	return result

#Search the XML
def interpret(results, xml, nots, element, attribute, fromElement, fromAttribute, whereElement, whereAttribute, operator, literal, order, orderElement, orderAttribute, number):
	root=None
	addHeader = True
	result=[]
	if(results.n):										#no header
		addHeader=False
	else:												#add xml header
		addHeader=True	
		
	if(fromElement!="" or fromAttribute!=""):			#got actual from, go search
		if(fromElement=="ROOT" and fromAttribute==""): 	#got ROOT
			root=xml.getroot()
		elif(fromElement!="" and fromAttribute==""):	#element only
			if(xml.getroot().tag == fromElement):
				root=xml.getroot()
			else:	
				root=xml.find(fromElement)				#changed findall to find, seems to be working like this, vlidate?
		elif(fromElement=="" and fromAttribute!=""):	#attribute only
			for elementCounter in list(searchSubElemsRecAll(xml.getroot(),[])):
				if(fromAttribute in elementCounter.attrib):
					root=elementCounter
					break						
		elif(fromElement!="" and fromAttribute!=""):	#element and attribute
			for elementCounter in xml.findall(fromElement):	
				if(fromAttribute in elementCounter.attrib and root==None):
					root=elementCounter
					break				
		if(root == []):								
			printError(80,"Syntax error: root element not found.\n") 
		result=searchSubElemsRec(root,element,result)
		if(whereElement!="" or whereAttribute!="" ):		#WHERE present in the query
			result=filterWhere(nots, result,whereElement,whereAttribute,operator,literal)
		if(order!=None):									#ORDER BY present in the query
			result=orderResult(result,order,orderElement,orderAttribute)		
		if(number != None):									#LIMIT present in the query
			number = int(number.getValue())					#convert to int
			if(number<0):
				printError(4,"LIMIT number cannot be a negative number.\n") 
			result=result[:number]
									
									
	
		
	if(results.root):									#got root to wrap the results
		document = ET.Element(results.root)
		for item in result:
			document.append(item)
		ET.ElementTree(document).write(results.output, encoding="utf-8", xml_declaration=addHeader)	
	else:												#no root
		document = ET.Element("@tmpRoot")
		for item in result:
			document.append(item)	
		try:	
			ET.ElementTree(document).write(results.output, encoding="utf-8", xml_declaration=addHeader)			
			file = open(results.output,'r')					
			text=file.read()
			file.close()
			file = open(results.output,'w')					
			text=re.sub(r'\<\@tmpRoot\>', "", text)
			text=re.sub(r'\<\/@tmpRoot\>', "", text)
			text=re.sub(r'<@tmpRoot />', "", text)
			file.write(text)
			file.close()
		except:
			printError(3,"Output permission error.\n")
	
#Analyzes the syntax of the query and executes
def parse(results):	
	try:
		inputFile = open(results.input,'r')			#open the xml file
	except:
		printError(2,"Input file open error.\n")
	try:
		xml = ET.parse(inputFile)
	except:
		exit(FORMAT_ERROR)
	inputFile.close()	
	text = getQuery(results)
	#Syntax analysis:
	nots=0
	element=""
	attribute=""
	fromElement=""
	fromAttribute=""
	whereElement=""
	whereAttribute=""
	operator=None
	literal=None
	order=None
	orderElement=""
	orderAttribute=""
	number=None
	
	token = getToken(text)	
	#SELECT
	if(token.getType() == TOKEN_SELECT):
		token = getToken(text)
	else:
		printError(80,"Syntax error: first token not SELECT\n")
	#ELEMENT	
	if(token.getType() == TOKEN_ELEMENT and token.getValue().count(".") < 2):
		if("." in token.getValue()):			#is there dot in token?
			printError(80,"Syntax error: expected element after SELECT, but there was a dot in there for some reason.\n")
		else:								#element
			element=token.getValue()
	else:
		printError(80,"Syntax error: second token not element\n")
	token = getToken(text)	
	#FROM
	if(token.getType() != TOKEN_FROM):
		printError(80,"Syntax error: third token not FROM\n")
	token = getToken(text)	
	#<From-elm>
	if(token.getType() == TOKEN_ELEMENT and token.getValue().count(".") < 2):	#3rd is element
		if("." in token.getValue()):			#is there dot in token?
			if(token.getValue()[0] == "."): 		#.attribute
				fromAttribute=token.getValue()[1:]
			else:								#element.attribute
				tmp=token.getValue().split(".")
				fromElement=tmp[0]
				fromAttribute=tmp[1]	
		else:								#element
			fromElement=token.getValue()
		token = getToken(text)		
	elif(token.getType() == TOKEN_ROOT):	#3rd is ROOT
		fromElement="ROOT"
		token = getToken(text)	
	#<WHERE-CLAUSE>
	if(token.getType() == TOKEN_WHERE):		#Where found
		nots=0
		token = getToken(text)
		while(token.getType() == TOKEN_NOT):
			nots+=1
			token = getToken(text)
		if(token.getType() == TOKEN_ELEMENT and token.getValue().count(".") < 2):
			if("." in token.getValue()):			#is there dot in token?
				if(token.getValue()[0] == "."): 		#.attribute
					whereAttribute=token.getValue()[1:]
				else:								#element.attribute
					tmp=token.getValue().split(".")
					whereElement=tmp[0]
					whereAttribute=tmp[1]	
			else:								#element
				whereElement=token.getValue()	
		else:
			printError(80,"Syntax error: no element in where clause\n")
		token = getToken(text)	
		if(token.getType() == TOKEN_CONTAINS or token.getType() == TOKEN_LESS or token.getType() == TOKEN_GREATER or token.getType() == TOKEN_EQUAL):	#operator
			operator=token
		else:
			printError(80,"Syntax error: no operator in where clause\n")
		token = getToken(text)	
		if(token.getType() == TOKEN_NUMBER or token.getType()==TOKEN_STRING):
			literal=token
		else:
			printError(80,"Syntax error: string or number expected after oprator\n")
		token = getToken(text)
	#<ORDER-CLAUSE>
	if(token.getType() == TOKEN_ORDER):
		token = getToken(text)
		if(token.getType() == TOKEN_BY):
			token = getToken(text)
			if(token.getType() == TOKEN_ELEMENT and token.getValue().count(".") < 2):
				if("." in token.getValue()):			#is there dot in token?
					if(token.getValue()[0] == "."): 		#.attribute
						orderAttribute=token.getValue()[1:]
					else:								#element.attribute
						tmp=token.getValue().split(".")
						orderElement=tmp[0]
						orderAttribute=tmp[1]	
				else:								#element
					orderElement=token.getValue()	
			else:
				printError(80,"Syntax error: no element in order clause\n")
			token = getToken(text)
			if(token.getType() == TOKEN_ASC or token.getType() == TOKEN_DESC):	
				order=token
				token = getToken(text)
			else:
				printError(80,"Syntax error: ASC or DESC expected in order clause\n")
		else:
			printError(80,"Syntax error: ORDER not followed by BY\n")
	#<LIMITn>
	if(token.getType() == TOKEN_LIMIT):
		token = getToken(text)
		if(token.getType() == TOKEN_NUMBER):
			number = token
			token = getToken(text)
		else:
			printError(80,"Syntax error: no number after LIMIT\n")	
	if(token.getType() != TOKEN_EOF):
		printError(80,"Syntax error: EOL expected\n")	
	#call the interpreter
	interpret(results, xml, nots, element, attribute, fromElement, fromAttribute, whereElement, whereAttribute, operator, literal, order, orderElement, orderAttribute, number)
					
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
exit(0)
