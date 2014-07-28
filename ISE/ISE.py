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

print 'Irish Stock Exchange'
standardname = 'ISE.xml'
site = 'https://www.isedirect.ie/LeiFiles/'
folder = sys.argv[1] + 'LOUs/ISE/'
ell = sys.argv[1] + 'Scripts/charlist.txt'
cdl = sys.argv[1] + 'Scripts/countrydict.txt'
date = sys.argv[2]
year = str(date)[2:4]
month = str(date)[4:6]
day = str(date)[6:8]
iseformat = day + '-' + month + '-' + year
if sys.argv[3] == 'true':
	prefix = 'LeiDaily_'
else:
	prefix = 'LeiDelta_'

#Counters
regnumber = 0
geoattempts = 0
geoerrors = 0
bingcount = 0
yahoocount = 0

dictfile = open('CountryDict.txt', 'r')
countrydict = eval(dictfile.read())
#countrydict = {'AF' : 'Afghanistan', 'AL' : 'Albania', 'DZ' : 'Algeria', 'AS' : 'American Samoa', 'AD' : 'Andorra', 'AO' : 'Angola', 'AI' : 'Anguilla', 'AQ' : 'Antarctica', 'AG' : 'Antigua and Barbuda', 'AR' : 'Argentina', 'AM' : 'Armenia', 'AW' : 'Aruba', 'AU' : 'Australia', 'AT' : 'Austria', 'AZ' : 'Azerbaijan', 'BS' : 'Bahamas', 'BH' : 'Bahrain', 'BD' : 'Bangladesh', 'BB' : 'Barbados', 'BY' : 'Belarus', 'BE' : 'Belgium', 'BZ' : 'Belize', 'BJ' : 'Benin', 'BM' : 'Bermuda', 'BT' : 'Bhutan', 'BO' : 'Bolivia', 'BA' : 'Bosnia and Herzegovina', 'BW' : 'Botswana', 'BV' : 'Bouvet Island', 'BR' : 'Brazil', 'IO' : 'British Indian Ocean Territory', 'BN' : 'Brunei Darussalam', 'BG' : 'Bulgaria', 'BF' : 'Burkina Faso', 'BI' : 'Burundi', 'KH' : 'Cambodia', 'CM' : 'Cameroon', 'CA' : 'Canada', 'CV' : 'Cape Verde', 'KY' : 'Cayman Islands', 'CF' : 'Central African Republic', 'TD' : 'Chad', 'CL' : 'Chile', 'CN' : 'China', 'CX' : 'Christmas Island', 'CC' : 'Cocos (Keeling Islands)', 'CO' : 'Colombia', 'KM' : 'Comoros', 'CG' : 'Congo', 'CK' : 'Cook Islands', 'CR' : 'Costa Rice', 'CI' : 'Ivory Coast', 'HR' : 'Croatia (Hrvatska)', 'CU' : 'Cuba', 'CW' : 'CuraÃ§ao', 'CY' : 'Cyprus', 'CZ' : 'Czech Republic', 'DK' : 'Denmark', 'DJ' : 'Djibouti', 'DM' : 'Dominica', 'DO' : 'Dominican Republic', 'TP' : 'East Timor', 'EC' : 'Ecuador', 'EG' : 'Egypt', 'SV' : 'El Salvador', 'GQ' : 'Equatorial Guinea', 'ER' : 'Eritrea', 'EE' : 'Estonia', 'ET' : 'Ethiopia', 'FK' : 'Falkland Islands (Malvinas)', 'FO' : 'Faroe Islands', 'FJ' : 'Fiji', 'FI' : 'Finland', 'FR' : 'France', 'FX' : 'France, Metropolitan', 'GB' : 'United Kingdom', 'GF' : 'French Guiana', 'PF' : 'French Polynesia', 'TF' : 'French Southern Territories', 'GA' : 'Gabon', 'GM' : 'Gambia', 'GE' : 'Georgia', 'DE' : 'Germany', 'GH' : 'Ghana', 'GI' : 'Gibraltar', 'GR' : 'Greece', 'GL' : 'Greenland', 'GD' : 'Grenada', 'GP' : 'Guadeloupe', 'GU' : 'Guam', 'GT' : 'Guatemala', 'GN' : 'Guinea', 'GW' : 'Guinea-Bissau', 'GY' : 'Guyana', 'HT' : 'Haiti', 'HM' : 'Heard and McDonald Islands', 'HN' : 'Honduras', 'HK' : 'Hong Kong', 'HU' : 'Hungary', 'IS' : 'Iceland', 'IN' : 'India', 'ID' : 'Indonesia', 'IR' : 'Iran', 'IQ' : 'Iraq', 'IE' : 'Ireland', 'IL' : 'Israel', 'IT' : 'Italy', 'JM' : 'Jamaica', 'JP' : 'Japan', 'JO' : 'Jordan', 'KZ' : 'Kazakhstan', 'KE' : 'Kenya', 'KI' : 'Kiribati', 'KP' : 'North Korea', 'KR' : 'South Korea', 'KW' : 'Kuwait', 'KG' : 'Kyrgyzstan', 'LA' : 'Laos', 'LV' : 'Latvia', 'LB' : 'Lebanon', 'LS' : 'Lesotho', 'LR' : 'Liberia', 'LY' : 'Libya', 'LI' : 'Liechtenstein', 'LT' : 'Lithuania', 'LU' : 'Luxembourg', 'MO' : 'Macau', 'MK' : 'Macedonia', 'MG' : 'Madagascar', 'MW' : 'Malawi', 'MY' : 'Malaysia', 'MV' : 'Maldives', 'ML' : 'Mali', 'MT' : 'Malta', 'MH' : 'Marshall Islands', 'MQ' : 'Martinique', 'MR' : 'Mauritania', 'MU' : 'Mauritius', 'YT' : 'Mayotte', 'MX' : 'Mexico', 'FM' : 'Micronesia', 'MD' : 'Moldova', 'MC' : 'Monaco', 'MN' : 'Mongolia', 'MS' : 'Montserrat', 'MA' : 'Morocco', 'MZ' : 'Mozambique', 'MM' : 'Myanmar', 'NA' : 'Namibia', 'NR' : 'Nauru', 'NP' : 'Nepal', 'NL' : 'Netherlands', 'AN' : 'Netherlands Antilles', 'NC' : 'New Caledonia', 'NZ' : 'New Zealand', 'NI' : 'Nicaragua', 'NE' : 'Niger', 'NG' : 'Nigeria', 'NU' : 'Niue', 'NF' : 'Norfolk Island', 'MP' : 'Northern Mariana Islands', 'NO' : 'Norway', 'OM' : 'Oman', 'PK' : 'Pakistan', 'PW' : 'Palau', 'PA' : 'Panama', 'PG' : 'Papua New Guinea', 'PY' : 'Paraguay', 'PE' : 'Peru', 'PH' : 'Philippines', 'PN' : 'Pitcairn', 'PL' : 'Poland', 'PT' : 'Portugal', 'PR' : 'Puerto Rico', 'QA' : 'Qatar', 'RE' : 'Reunion', 'RO' : 'Romania', 'RU' : 'Russian Federation', 'RW' : 'Rwanda', 'KN' : 'Saint Kitts and Nevis', 'LC' : 'Saint Lucia', 'VC' : 'Saint Vincent and the Grenadines', 'WS' : 'Samoa', 'SM' : 'San Marino', 'ST' : 'Sao Tome and Principe', 'SA' : 'Saudi Arabia', 'SN' : 'Senegal', 'SC' : 'Seychelles', 'SL' : 'Sierra Leone', 'SG' : 'Singapore', 'SK' : 'Slovak Republic', 'SI' : 'Slovenia', 'SB' : 'Solomon Islands', 'SO' : 'Somalia', 'ZA' : 'South Africa', 'GS' : 'S. George and S. Sandwich Islands', 'ES' : 'Spain', 'LK' : 'Sri Lanka', 'SH' : 'St. Helena', 'PM' : 'St. Pierre and Miquelon', 'SD' : 'Sudan', 'SR' : 'Suriname', 'SJ' : 'Svalbard and Jan Mayen Islands', 'SZ' : 'Swaziland', 'SE' : 'Sweden', 'CH' : 'Switzerland', 'SY' : 'Syria', 'TW' : 'Taiwan', 'TJ' : 'Tajikistan', 'TZ' : 'Tanzania', 'TH' : 'Thailand', 'TG' : 'Togo', 'TK' : 'Tokelau', 'TO' : 'Tonga', 'TT' : 'Trinidad and Tobago', 'TN' : 'Tunisia', 'TR' : 'Turkey', 'TM' : 'Turkmenistan', 'TC' : 'Turks and Caicos Islands', 'TV' : 'Tuvalu', 'UG' : 'Uganda', 'UA' : 'Ukraine', 'AE' : 'United Arab Emirates', 'UK' : 'United Kingdom', 'US' : 'United States', 'UM' : 'US Minor Outlying Islands', 'UY' : 'Uruguay', 'UZ' : 'Uzbekistan', 'VU' : 'Vanuatu', 'VA' : 'Vatican City State (Holy See)', 'VE' : 'Venezuela', 'VN' : 'Vietnam', 'VG' : 'British Virgin Islands', 'VI' : 'US Virgin Islands', 'WF' : 'Wallis and Futuna Islands', 'EH' : 'Western Sahara', 'YE' : 'Yemen', 'YU' : 'Yugoslavia', 'ZR' : 'Zaire', 'ZM' : 'Zambia', 'ZW' : 'Zimbabwe', 'GG' : 'Guernsey', 'JE' : 'Jersey', 'IM' : 'Isle of Man', 'Un' : 'United Kingdom', 'Ja' : 'Japan', 'Bu' : 'Bulgaria', 'Sw' : 'Switzerland', 'RS' : 'Serbia', 'Po' : 'Poland', 'Sp' : 'Spain', 'Ho' : 'Hong Kong', 'Me' : 'Mexico', 'Tu' : 'Turkey', 'BL' : 'Saint Barthélemy', 'Ko' : 'South Korea', 'Ta' : 'Taiwan'}

print "Searching for '" + prefix + "'..."
filename = prefix + iseformat + '.xml'
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
ET.register_namespace('lei', 'www.isedirect.ie')
root = tree.getroot()

#Find the subelements that make up the RegisteredAddress subelement 
for LegalEntity in root.findall('{www.isedirect.ie}LegalEntity'):
	regnumber = regnumber + 1
	LEI = LegalEntity.find('{www.isedirect.ie}LEI')
	RegisteredAddress = LegalEntity.find('{www.isedirect.ie}RegisteredAddress')
	a1 = RegisteredAddress.find('{www.isedirect.ie}AddressLineOne')
	try:
		a2 = RegisteredAddress.find('{www.isedirect.ie}AddressLineTwo')
	except:
		pass
	try:
		a3 = RegisteredAddress.find('{www.isedirect.ie}AddressLineThree')
	except:
		pass	
	try:
		a4 = RegisteredAddress.find('{www.isedirect.ie}AddressLineFour')
	except:
		pass	
	country = RegisteredAddress.find('{www.isedirect.ie}Country')

#Replace country codes with country names
	country.text = leifix.countryfix(country.text, cdl)	

#Combine all RegisteredAddress' subelements' text into a single address
	list = [a1, a2, a3, a4, country]
	addrs = 'something is not working'
	for tag in list:
		#Check if there is no data in the element, ignore if there is none
		if tag != None:
			if tag.text != None:
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
						if addrs.endswith(', '):
							addrs = addrs + tag.text
						elif addrs.endswith(','):
							addrs = addrs + " " + tag.text
						else:
							addrs = addrs + ", " + tag.text

#Add Address subelements to the LegalEntity element	
	Address = ET.SubElement(LegalEntity, '{www.isedirect.ie}Address')
	Address.text = addrs
	
	#print Address.text

#Add Geolocation subelement to the LegalEntity element, and lat and long subelement to geolocation element	
	Geolocation = ET.SubElement(LegalEntity, '{www.isedirect.ie}Geolocation')
	Latitude = ET.SubElement(Geolocation, '{www.isedirect.ie}Latitude')
	Longitude = ET.SubElement(Geolocation, '{www.isedirect.ie}Longitude')
		
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
log = open(sys.argv[1] + 'LOUs/ISE/ISE.log', 'w')
log.write(date)
log.close()
