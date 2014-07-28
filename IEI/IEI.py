#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#FTP file transfer using ftplib
#Dictionary lookup using re
#Today's date determined using datetime
#Geocoding using geopy

import sys
import ftplib
import csv
sys.path.append(sys.argv[1]+'Scripts/')
import leifix

print 'London Stock Exchange'
standardname = 'IEI.csv'
host = 'data-x.londonstockexchange.com'
directory = 'BespokeDownloads/pre_LOU/'
username = 'LSESTAGING\LEI2204244'
password = '1508CnpE'
folder = sys.argv[1] + 'LOUs/IEI/'
ell = sys.argv[1] + 'Scripts/charlist.txt'
cdl = sys.argv[1] + 'Scripts/countrydict.txt'
date = sys.argv[2]
if sys.argv[3] == 'true':
	prefix = 'IEI_Full_File_'
else:
	prefix = 'IEI_Daily_Changes_'

#Counters
regnumber = 0
rowcount = 0
geoattempts = 0
geoerrors = 0
bingcount = 0
yahoocount = 0

#Connect to FTP server
print "Connecting to server..."

ftp = ftplib.FTP(host, username, password)
ftp.set_pasv(False)
ftp.set_debuglevel(2)

print "Searching for '" + prefix + "'..."
filename = prefix + date + '.txt'
ftp.cwd(directory)

#Download the file
print 'Downloading...'
lf = open(folder+'Downloads/'+filename, 'wb')
ftp.retrbinary("RETR "+filename, lf.write)
ftp.quit()
lf.close()

print 'Complete'

#Create dictionary of previous LEI files to get GPS coordinates
latdictionary = leifix.dictmaker(sys.argv[1]+'Scripts/Final.csv', 0, 9)
longdictionary = leifix.dictmaker(sys.argv[1]+'Scripts/Final.csv', 0, 10)

#Open and parse CSV
ifile = open(folder+'Downloads/'+filename,'rb')
reader=csv.reader(ifile, delimiter='|')
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
		
		row[11] = leifix.countryfix(row[11], cdl)	
		
		list = [row[6], row[7], row[8], row[11], row[10]]
		addrs = 'something is not working'
		for tag in list:
			if tag != "":
				#Check if the element contains non-useable information, ignore if it does
				if tag.startswith(('C/O', 'LEVEL', 'UNIT', 'FLOOR', 'SUITE', 'THE', 'CORPORATION')) or tag.endswith(('FLOOR', 'LTD', 'CENTER', 'CENTRE')):
					#Used for the scenario where the tag starts with non-useable string yet still contains the entire address. 
					#This should only happen when 'AddressLineOne' is the only field being used.
					if tag.endswith(tuple('0123456789')):
						if addrs == 'something is not working':
							#Start the final address text with the text of the current element
							addrs = tag
						else:
							pass
					else:
						if tag.startswith('UNITED'):
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

		#print addrs
		row.append(addrs)
		
		#Get GPS coordinates, first by looking up old file, then by using the internet
		try:
			#LEI Lookup:
			geo = leifix.lookup(row[1], latdictionary, longdictionary)
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
		#print geo[0] + ", " + geo[1]
	
	writer.writerow(row)
	rowcount = rowcount + 1
	
print "Number of Registrations: " + str(regnumber)
print "Number of Gecoding Attemtps: " + str(geoattempts)
print "Number of Geocoding Errors: " + str(geoerrors)

ifile.close()
ofile.close()
#Create/add to log file
log = open(sys.argv[1] + 'LOUs/IEI/IEI.log', 'w')
log.write(date)
log.close()