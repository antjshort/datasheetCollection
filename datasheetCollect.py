import sys
import json
import urllib
import csv
import time

DEBUG = 0

def buildURL(mpnStr):
	url = 'http://octopart.com/api/v3/parts/match?'
	url += '&queries=[{"mpn":"'
	url += mpnStr
	url += '"}]'
	url += '&apikey=9d099e82'
	url += '&include=datasheets'

	if DEBUG:
		print ('%s\nurl: %s\n' % (mpnStr, url))

	return url

def extractMpns(inputFile, columnHeader, mpnList):
	with open(inputFile, 'rb') as csvFile:
		data = dict(enumerate(csv.DictReader(csvFile)))
	 	for k, v in data.items():
	 		#Add valid non-empty MPNs
	 		if v[columnHeader]:
	 			mpnList.append(v[columnHeader])

	 	if DEBUG:
			print mpnList

def getDatasheetURL(dataSheetItem, mpn, mpnDatasheetsDict):
	for member in dataSheetItem:
		if member['url']:			
			if member['url'][-3:] == "pdf":
				if DEBUG:
					print member['url']
				mpnDatasheetsDict[mpn] = member['url']
				break
		else:
				print ('%s datasheet could not be found.' % mpn)

def parseResponseForDatasheet(response, mpn, mpnDatasheetsDict):	
	for result in response['results']:

		if not result['items']:
				print ('%s datasheet could not be found.' % mpn)

 		else:
		   for item in result['items']:

	   		if not item['datasheets']:
	 				print ('%s datasheet could not be found.' % mpn)
	 				break

	   		else:	
	   			getDatasheetURL(item['datasheets'], mpn, mpnDatasheetsDict)  					

def retrieveURL(url):
	data = urllib.urlopen(url).read()
	response = json.loads(data)
	if DEBUG:
		print response['msec']
	return response

def main ():
	try:
		inputCsv = sys.argv[1]
		columnHeader = sys.argv[2]
	except IndexError:
		print 'Error - argument1: nameOfCSV.csv, argument2: "Name of Column Header Containing MPN"'
		sys.exit()

	mpnList = []

	extractMpns(inputCsv, columnHeader, mpnList)

	mpnDatasheets = {}

	for mpn in mpnList:
		url=buildURL(mpn)

		response = retrieveURL(url)

		parseResponseForDatasheet(response, mpn, mpnDatasheets)
		
		time.sleep(0.350)	 				
	
	print "\n     MPN     | Link to datasheet .pdf"	
	for k,v in mpnDatasheets.items():
		print ('%s | %s' % (k, v)) 		

if __name__ == "__main__":
	main()