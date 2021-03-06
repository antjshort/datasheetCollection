import sys
import json
import urllib
import requests
import csv
import time
import shutil

DEBUG = 0

#Query octopart.com API using manufacturer part number
def buildURL(mpnStr):
    url = 'http://octopart.com/api/v3/parts/match?'
    url += '&queries=[{"mpn":"'
    url += mpnStr
    url += '"}]'
    url += '&apikey=INSERT_KEY'
    url += '&include=datasheets'
    if DEBUG:
        print ('%s\nurl: %s\n' % (mpnStr, url))

    return url
#Iterate through CSV column for manufacturer part numbers, store #s to list
def extractMpns(inputFile, columnHeader, mpnList):
    with open(inputFile, 'rb') as csvFile:
        data = dict(enumerate(csv.DictReader(csvFile)))
        for k, v in data.items():
		#Add valid non-empty MPNs
            if v[columnHeader]:
                mpnList.append(v[columnHeader])
    if DEBUG:
        print mpnList
#Iterate through datasheet json element for 'url' child, extract only urls pointing to .pdf files
def getDatasheetURL(dataSheetItem, mpn, mpnDatasheetsDict):
    for member in dataSheetItem:
        if member['url']:
            fileType = getFileType(member['url'])
            if fileType == 'pdf' or fileType == 'docx' or fileType == 'doc':
                if DEBUG:
                    print fileType
                    print member['url']
                mpnDatasheetsDict[mpn] = member['url']
                break
            else:
                 if DEBUG:
                     print ('%s contains no datasheet URL.' % mpn)   
#Iterate through json response from mpn search query
def parseResponseForDatasheet(response, mpn, mpnDatasheetsDict):
	try:	
		for result in response['results']:
			#no valid json data
			if not result['items']:
				if DEBUG:
					print ('%s query returned no results.' % mpn)
			else:
				for item in result['items']:
					#valid json data, but no datasheets element
					if not item['datasheets']:
						if DEBUG:
							print ('%s datasheet could not be found.' % mpn)
							break
					#extract and store the datasheet url
					else:
						getDatasheetURL(item['datasheets'], mpn, mpnDatasheetsDict)
	except KeyError:
		print 'Key Error \nResponse: ', response

#Extract and return json response from url 
def retrieveURL(url):
    data = urllib.urlopen(url).read()
    response = json.loads(data)
    if DEBUG:
        print response['msec']

    return response
#Print manufacturer part numbers and their associated datasheet URL
def printDataSheetURLs(mpnDatasheetsDict):
    print "\n     MPN     | Link to datasheet"	
    for k,v in mpnDatasheetsDict.items():
        print ('%s | %s' % (k, v))
#Extract filetype from string
def getFileType(downloadURL):
    urlStr = downloadURL.split('.')
    return str(urlStr[len(urlStr) - 1])
#Remove illegal characters and add file type extension        
def cleanFilename(filename, downloadURL):
    #remove illegal characters
    filename = filename.translate(None, r'<>:"/\|?*')
    fileType = getFileType(downloadURL)
    filename = filename + '.' + fileType    
    if DEBUG:
        print filename
        
    return filename
#Download and store PDF to /Files directory
def downloadFile(filename, download_url, fileDir):
    filename = cleanFilename(filename, download_url)
    #Retrieve url
    r = requests.get(download_url,stream=True)
    r.raw.decode_content = True
    #Copy and store data	
    with open(fileDir + "\\" + filename, 'wb') as f:
        shutil.copyfileobj(r.raw, f) 

def main ():
    try:
        inputCsv = sys.argv[1]
        columnHeader = sys.argv[2]
        outputFilesDir = sys.argv[3]
    except IndexError:
         print """
         Error - 
         argument1: nameOfCSV.csv
         argument2: "Name of Column Header Containing MPN"
         argument3: nameOfOutputFileFolder
         e.g. datasheetCollect.py datasheets.csv "Vendor Part Number" Files
         """
         sys.exit()
    print 'Powered by Octopart - www.octopart.com'
    #Empty list to store all manufacturer part numbers currently missing datasheets
    mpnList = []
    #Retrieve the misisng manufacturer part numbers from input file
    print 'Extracting MPNs from CSV input file...'
    extractMpns(inputCsv, columnHeader, mpnList)
    print 'Total MPNs found: ', len(mpnList)
    #Empty dictionary to store mpns and datasheet urls
    mpnDatasheets = {}
    print 'Searching database for MPN datasheet URLs...'
    for mpn in mpnList:
        url = buildURL(mpn)
        #Open url and retrieve json response
        response = retrieveURL(url)
        #Parse the response for datasheet urls
        parseResponseForDatasheet(response, mpn, mpnDatasheets)
        #API Rule: Do not query more than 3/s
        time.sleep(0.350) 				
	
    print ('MPN datasheets URLs found: %s/%s' % (len(mpnDatasheets),len(mpnList)))
    print 'Downloading datasheets...'
    for k,v in mpnDatasheets.items():
        downloadFile(k, v, outputFilesDir)
    
    print 'Complete'
    
if __name__ == "__main__":
    main()
