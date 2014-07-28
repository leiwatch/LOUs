#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#Web lookup using re, datetime, and BeautifulSoup
#Web scraping using urllib and BeautifulSoup
#Unzipping using zipfile
#XML parsing using ElementTree
#Geocoding using geopy

import sys
import re
import urllib
import zipfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
sys.path.append(sys.argv[1]+'Scripts/')
import leifix

print 'DTCC/Swift'
standardname = 'GMEI.xml'
site = 'ftp://ftp.ciciutility.org/GMEIIssuedFiles/'
folder = sys.argv[1] + 'LOUs/GMEI/'
ell = sys.argv[1] + 'Scripts/charlist.txt'
cdl = sys.argv[1] + 'Scripts/countrydict.txt'
date = sys.argv[2]
if sys.argv[3] == 'true':
	prefix = 'GMEIIssuedFullFile_'
else:
	prefix = 'GMEIIssuedDeltaFile_'

#Counters
regnumber = 0
geoattempts = 0
geoerrors = 0
bingcount = 0
yahoocount = 0

print "Searching for '" + prefix + "'..."
# Read from the object, storing the page's contents in 'htmlcontent'.
webpage = urllib.urlopen(site)
htmlcontent = webpage.read()
webpage.close()

#Turn html into soup object
soup = BeautifulSoup(htmlcontent)

#Search all strings in the soup object for a string the matches name of the deltafile using date and regex
for s in soup.strings:
	file = re.search(prefix+date+'\D'+'\d{6}', s)
	if file:
		print 'Found: ' + file.group(0)
		filename = file.group(0) + '.zip'
		url = site + filename
		#Download the file
		print 'Downloading...'
		urllib.urlretrieve(url, folder+'Downloads/'+filename)
		print 'Complete'
		#Extract the zip file
		zf = zipfile.ZipFile(folder+'Downloads/'+filename)
		print 'Extracting...'
		zf.extractall(folder+'Downloads/')
		print 'Complete'
		for l in zf.infolist():
			xmlfile = l.filename

#Create dictionary of previous LEI files to get GPS coordinates
latdictionary = leifix.dictmaker(sys.argv[1]+'Scripts/Final.csv', 0, 9)
longdictionary = leifix.dictmaker(sys.argv[1]+'Scripts/Final.csv', 0, 10)

#Parse xml file
tree = ET.parse(folder+'Downloads/'+xmlfile)
ET.register_namespace('lei', 'www.leiutility.org')
root = tree.getroot()

#Find the subelements that make up the RegisteredAddress subelement 
for LegalEntity in root.findall('{www.leiutility.org}LegalEntity'):
	regnumber = regnumber + 1
	LEI = LegalEntity.find('{www.leiutility.org}LEI')
	RegisteredAddress = LegalEntity.find('{www.leiutility.org}RegisteredAddress')
	a1 = RegisteredAddress.find('{www.leiutility.org}AddressLineOne')
	a2 = RegisteredAddress.find('{www.leiutility.org}AddressLineTwo')
	a3 = RegisteredAddress.find('{www.leiutility.org}AddressLineThree')
	a4 = RegisteredAddress.find('{www.leiutility.org}AddressLineFour')
	city = RegisteredAddress.find('{www.leiutility.org}City')
	state = RegisteredAddress.find('{www.leiutility.org}State')
	country = RegisteredAddress.find('{www.leiutility.org}Country')
	postcode = RegisteredAddress.find('{www.leiutility.org}PostCode')
	
#Replace country codes with country names
	country.text = leifix.countryfix(country.text, cdl)

#Combine all RegisteredAddress' subelements' text into a single address
	list = [a1, a2, a3, a4, city, state, country]
	addrs = 'something is not working'
	for tag in list:
		#Check if there is no data in the element, ignore if there is none
		if tag != None:
			#Fix encoding
			tag.text = leifix.encodingfix(tag.text, ell, 'utf-8')
			
			#Check if the element contains non-useable information, ignore if it does
			if tag.text.startswith(('C/O', 'c/o', 'Level', 'Unit', 'Floor', 'Suite', 'The', 'Corporation')) or tag.text.endswith(('Floor', 'Ltd', 'Center', 'Centre')):
				#Used for the scenario where the tag starts with non-useable string yet still contains the entire address. 
				#This should only happen when 'AddressLineOne' is the only field being used.
				if tag.text.endswith(tuple('0123456789')):
					if addrs == 'something is not working':
						#Start the final address text with the text of the current element
						addrs = tag.text
					else:
						pass
				else:
					if tag.text.startswith('United'):
						addrs = addrs + ", " + tag.text
					else:
						pass
			else:
				if addrs == 'something is not working':
					#Start the final address text with the text of the current element
					addrs = tag.text
				else:
					#Combine each element text to the final address text
					addrs = addrs + ", " + tag.text

#Add Address subelements to the LegalEntity element	
	Address = ET.SubElement(LegalEntity, '{www.leiutility.org}Address')
	Address.text = addrs
	#print addrs

#Add Geolocation subelement to the LegalEntity element, and lat and long subelement to geolocation element	
	Geolocation = ET.SubElement(LegalEntity, '{www.leiutility.org}Geolocation')
	Latitude = ET.SubElement(Geolocation, '{www.leiutility.org}Latitude')
	Longitude = ET.SubElement(Geolocation, '{www.leiutility.org}Longitude')

#Get GPS coordinates, first by looking up old file, then by using the internet
	try:
		#LEI Lookup:
		geo = leifix.lookup(LEI.text, latdictionary, longdictionary)
		Latitude.text = geo[0]
		Longitude.text = geo[1]
	except:
		#Geocoding:
		geo = leifix.geocoder(addrs, bingcount, yahoocount)
		Latitude.text = geo[0]
		Longitude.text = geo[1]
		#Bingcount and Yahoocount are passed back and forth with leifix.geocoder function in order to cycle through user keys
		bingcount = geo[2]
		yahoocount = geo[3]
		#Count geocoding errors
		geoattempts = geoattempts + 1
		if geo[0] == "N/A":
			geoerrors = geoerrors + 1

print "Number of New Registrations: " + str(regnumber)	
print "Number of Gecoding Attemtps: " + str(geoattempts)
print "Number of Geocoding Errors: " + str(geoerrors)

#Output to and XML file
tree.write(folder+standardname, encoding='utf-8')
#Create/add to log file
log = open(sys.argv[1] + 'LOUs/GMEI/GMEI.log', 'w')
log.write(date)
log.close()
