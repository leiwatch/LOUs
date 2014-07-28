#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#Web scraping using urllib
#Dictionary lookup using re
#Geocoding using geopy

import sys
import datetime
import urllib
import re
import csv
sys.path.append(sys.argv[1]+'Scripts/')
import leifix


print 'Dutch Chamber of Commerce'
standardname = 'KVK.csv'
site = 'http://www.kvk.nl/download/'
folder = sys.argv[1] + 'LOUs/KVK/'
cdl = sys.argv[1] + 'Scripts/countrydict.txt'
ell = sys.argv[1] + 'Scripts/charlist.txt'
date = sys.argv[2]
year = int(date[0:4])
month = int(date[4:6])
day = int(date[6:8])
deltadate = (datetime.date.today() - datetime.date(year, month, day)).days
if sys.argv[3] == 'true':
	prefix = 'LEI_Full_tcm109-'
	suffix = str(377398+deltadate)
else:
	prefix = 'LEI_'
	suffix = str(1+deltadate)+'_tcm109-'+str(377399+deltadate)
filename = prefix + suffix + '.csv'

#Counters
regnumber = 0
rowcount = 0
geoattempts = 0
geoerrors = 0
bingcount = 0
yahoocount = 0

#Download the file
print "Searching for '" + prefix + suffix + "'..."
url = site + filename
print 'Downloading...'
urllib.urlretrieve(url, folder+'Downloads/'+filename)
print 'Complete'

#Create dictionary of previous LEI files to get GPS coordinates
latdictionary = leifix.dictmaker(sys.argv[1]+'Scripts/Final.csv', 0, 9)
longdictionary = leifix.dictmaker(sys.argv[1]+'Scripts/Final.csv', 0, 10)

#Open CSV
ifile = open(folder+'Downloads/'+filename,'rb')
reader=csv.reader(ifile, delimiter=';')
ofile = open(folder+standardname,'wb')
writer = csv.writer(ofile, delimiter=',', quotechar='"')

for row in reader:
	for r in row:
		r = leifix.encodingfix(r, ell, 'utf-8')
	
	if rowcount == 0:
		row.append('Address')
		row.append('Latitude')
		row.append('Longitude')
	else:
		regnumber = regnumber + 1
		
		row[22] = leifix.countryfix(row[22], cdl)
		
		list = [row[15], row[16], row[17], row[18], row[19], row[22], row[20]]
		addrs = 'something is not working'
		for tag in list:
			if tag != "":
				#Check if the element contains non-useable information, ignore if it does
				if tag.startswith(('C/O', 'c/o', 'Level', 'Unit', 'Floor', 'Suite', 'The', 'Corporation')) or tag.endswith(('Floor', 'Ltd', 'Center', 'Centre')):
					#Used for the scenario where the tag starts with non-useable string yet still contains the entire address. 
					#This should only happen when 'AddressLineOne' is the only field being used.
					if tag.endswith(tuple('0123456789')):
						if addrs == 'something is not working':
							#Start the final address text with the text of the current element
							addrs = tag
						else:
							pass
					else:
						if tag.startswith('United'):
							addrs = addrs + ", " + tag
						else:
							pass
				else:
					if addrs == 'something is not working':
						#Start the final address text with the text of the current element
						addrs = tag
					else:
						#Combine each element text to the final address text
						addrs = addrs + ", " + tag
						
		row.append(addrs)
		
		#Get GPS coordinates, first by looking up old file, then by using the internet
		try:
			#LEI Lookup:
			geo = leifix.lookup(row[0], latdictionary, longdictionary)
			row.append(geo[0])
			row.append(geo[1])
		except:
			#Geocoding:
			geo = leifix.geocoder(addrs, bingcount, yahoocount)
			row.append(geo[0])
			row.append(geo[1])
			#Bingcount and Yahoocount are passed back and forth with leifix.geocoder function in order to cycle through user keys
			bingcount = geo[2]
			yahoocount = geo[3]
			#Count geocoding errors
			geoattempts = geoattempts + 1
			if geo[0] == "N/A":
				geoerrors = geoerrors + 1
	
	writer.writerow(row)
	rowcount = rowcount + 1

print "Number of Registrations: " + str(regnumber)
print "Number of Gecoding Attemtps: " + str(geoattempts)
print "Number of Geocoding Errors: " + str(geoerrors)

ifile.close()
ofile.close()
#Create/add to log file
log = open(sys.argv[1] + 'LOUs/KVK/KVK.log', 'w')
log.write(date)
log.close()
