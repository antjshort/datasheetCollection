import json
import urllib

url = 'http://octopart.com/api/v3/parts/match?'
url += '&queries=[{"mpn":"SN74S74N"}]'
url += '&apikey=9d099e82'

data = urllib.urlopen(url).read()
response = json.loads(data)

# print request time (in milliseconds)
print response['msec']

# print mpn's
for result in response['results']:
    for item in result['items']:
        print item['mpn']
