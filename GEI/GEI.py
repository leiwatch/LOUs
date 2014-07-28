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
sys.path.append(sys.argv[1]+'Scripts/')
import leifix

print 'WM DatenService'
standardname = 'GEI.xml'
site = 'https://www.geiportal.org/customer/index.php?a=sea&act=download&lang='
folder = sys.argv[1] + 'LOUs/GEI/'
ell = sys.argv[1] + 'Scripts/charlist.txt'
cdl = sys.argv[1] + 'Scripts/countrydict.txt'
date = sys.argv[2]
if sys.argv[3] == 'true':
	prefix = 'FullFile_'
else:
	prefix = 'DeltaFile_'

#Counters
regnumber = 0
geoattempts = 0
geoerrors = 0
bingcount = 0
yahoocount = 0
		
#Attempt to download correct file by testing from a list of predetermined suffixes
print "Searching for '" + prefix + "'..."
suffixlist = ['003001', '003002', '005001', '005002']
for suffix in suffixlist:
	try:
		filename = prefix + date + suffix + '.zip'
		url = 'https://www.geiportal.org/customer/download_xml.php?file=' + filename
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
		break
	except:
		print "Failed to unzip " + filename + ". Moving to next file in list..."
		pass

#Create dictionary of previous LEI files to get GPS coordinates
latdictionary = leifix.dictmaker(sys.argv[1]+'Scripts/Final.csv', 0, 9)
longdictionary = leifix.dictmaker(sys.argv[1]+'Scripts/Final.csv', 0, 10)

#Parse xml file
tree = ET.parse(folder+'Downloads/' + xmlfile)
ET.register_namespace('gei', 'https://www.geiportal.org')
root = tree.getroot()

#Find the subelements that make up the RegisteredAddress subelement 
for LegalEntity in root.findall('{https://www.geiportal.org}LegalEntity'):	
	regnumber = regnumber + 1
	LEI = LegalEntity.find('{https://www.geiportal.org}GEI')
	LegalAddress = LegalEntity.find('{https://www.geiportal.org}CorporateLegalAddress')
	if LegalAddress == None:
		LegalAddress = LegalEntity.find('{https://www.geiportal.org}FundManagerAddress')
		if LegalAddress == None:
			LegalAddress = LegalEntity.find('{https://www.geiportal.org}PublicCorpLegalAddress')
	street = LegalAddress.find('{https://www.geiportal.org}Street')
	city = LegalAddress.find('{https://www.geiportal.org}City')
	stateregion = LegalAddress.find('{https://www.geiportal.org}StateRegion')
	country = LegalAddress.find('{https://www.geiportal.org}Country')
	postalcode = LegalAddress.find('{https://www.geiportal.org}PostalCode')

#Replace country codes with country names
	country.text = leifix.countryfix(country.text, cdl)	

#Combine all RegisteredAddress' subelements' text into a single address
	list = [street, city, country]
	addrs = 'something is not working'
	for tag in list:
		#Check if there is no data in the element, ignore if there is none
		if tag != None:
			if tag.text != None:
				tag.text = leifix.encodingfix(tag.text, ell, 'utf-8')
				
				if addrs == 'something is not working':
					#Start the final address text with the text of the current element
					addrs = tag.text
				else:
					#Combine each element text to the final address text
					addrs = addrs + ", " + tag.text
			
#Add Address subelements to the LegalEntity element	
	Address = ET.SubElement(LegalEntity, '{https://www.geiportal.org}Address')
	Address.text = addrs
	#print Address.text

#Add Geolocation subelement to the LegalEntity element, and lat and long subelement to geolocation element	
	Geolocation = ET.SubElement(LegalEntity, '{https://www.geiportal.org}Geolocation')
	Latitude = ET.SubElement(Geolocation, '{https://www.geiportal.org}Latitude')
	Longitude = ET.SubElement(Geolocation, '{https://www.geiportal.org}Longitude')

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
log = open(sys.argv[1] + 'LOUs/GEI/GEI.log', 'w')
log.write(date)
log.close()
