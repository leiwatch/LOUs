#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#Web lookup using datetime
#Web scraping using urllib
#XML parsing using ElementTree
#Dictionary lookup using re
#Geocoding using geopy

import sys
import re
import urllib
import zipfile
import xml.etree.ElementTree as ET
sys.path.append(sys.argv[1]+'Scripts/')
import leifix

print 'Takasbank'
standardname = 'Takas.xml'
site = 'http://www.takasbank.com.tr/en/LEITurkey/'
prefix = 'LEITurkey'
folder = sys.argv[1] + 'LOUs/Takas/'
ell = sys.argv[1] + 'Scripts/charlist.txt'
cdl = sys.argv[1] + 'Scripts/countrydict.txt'
date = sys.argv[2]
if sys.argv[3] == 'true':
	suffix = 'FullFile'
else:
	suffix = 'FullFile'

#Counters
regnumber = 0
geoattempts = 0
geoerrors = 0
bingcount = 0
yahoocount = 0

print "Searching for '" + suffix + "'..."
filename = prefix + date + suffix + '.xml'
url = site + filename
#Download the file
print 'Downloading...'
urllib.urlretrieve(url, folder+'Downloads/'+filename)
print 'Complete'

#Create dictionary of previous LEI files to get GPS coordinates
latdictionary = leifix.dictmaker(sys.argv[1]+'Scripts/Final.csv', 0, 9)
longdictionary = leifix.dictmaker(sys.argv[1]+'Scripts/Final.csv', 0, 10)

#Parse xml file
tree = ET.parse(folder+'Downloads/'+filename)
ET.register_namespace('trlei', 'http://www.takasbank.com.tr/eng/LEITurkey/schema.xsd')
root = tree.getroot()

#Find the subelements that make up the RegisteredAddress subelement 
LEIRegistrations = root.find('{http://www.takasbank.com.tr/eng/LEITurkey/schema.xsd}LEIRegistrations')
for LEIRegistration in LEIRegistrations.findall('{http://www.takasbank.com.tr/eng/LEITurkey/schema.xsd}LEIRegistration'):
	regnumber = regnumber + 1
	LEI = LEIRegistration.find('{http://www.takasbank.com.tr/eng/LEITurkey/schema.xsd}LegalEntityIdentifier')
	a1 = LEIRegistration.find('{http://www.takasbank.com.tr/eng/LEITurkey/schema.xsd}RegisteredAddress1')	
	city = LEIRegistration.find('{http://www.takasbank.com.tr/eng/LEITurkey/schema.xsd}RegisteredCity')
	country = LEIRegistration.find('{http://www.takasbank.com.tr/eng/LEITurkey/schema.xsd}RegisteredCountryCode')

#Replace country codes with country names
	country.text = leifix.countryfix(country.text, cdl)

#Combine all RegisteredAddress' subelements' text into a single address
	list = [a1, city, country]
	addrs = 'something is not working'
	for tag in list:
		#Check if there is no data in the element, ignore if there is none
		if tag != None:
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
	Address = ET.SubElement(LEIRegistration, '{http://www.takasbank.com.tr/eng/LEITurkey/schema.xsd}Address')
	Address.text = addrs

#Add Geolocation subelement to the LegalEntity element, and lat and long subelement to geolocation element	
	Geolocation = ET.SubElement(LEIRegistration, '{http://www.takasbank.com.tr/eng/LEITurkey/schema.xsd}Geolocation')
	Latitude = ET.SubElement(Geolocation, '{http://www.takasbank.com.tr/eng/LEITurkey/schema.xsd}Latitude')
	Longitude = ET.SubElement(Geolocation, '{http://www.takasbank.com.tr/eng/LEITurkey/schema.xsd}Longitude')

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
tree.write(folder+standardname)
#Create/add to log file
log = open(sys.argv[1] + 'LOUs/Takas/Takas.log', 'w')
log.write(date)
log.close()
