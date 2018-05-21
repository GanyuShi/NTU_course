import requests
import sqlite3
from bs4 import BeautifulSoup
import re


def parseCourse(table):
	print("==== START PARSING COURSE TABLE ====")
	#print(table)
	global ccode 
	ccode = table.find_all(attrs={"width": "100"})[0].string.strip()
	cname = table.find_all(attrs={"width": "500"})[0].string.strip()
	cau = table.find_all(attrs={"width": "50"})[0].string.strip()
	print ('course code:', ccode)
	print ('course name:', cname)
	print ('course AU:', cau)

	return (ccode, cname, cau)


def parseIndexRow(row):
	print("==== START PARSING INDEX ROW ====")

	'''cindex = row[0]
	ctype = row[1]
	cgroup = row[2]
	cday = row[3]
	ctime = row[4]
	cvenue = row[5]'''
	

	tdata = row.find_all('td')

	global cindex
	if not tdata[0].string is None:
		cindex = tdata[0].string
	ctype = tdata[1].string
	cgroup = tdata[2].string
	cday = tdata[3].string
	ctime = tdata[4].string
	cvenue = tdata[5].string
	cremark = tdata[6].string

	print('cindex:', cindex)
	print('ctype:', ctype)
	print('cgroup:', cgroup)
	print('cday:', cday)
	print('ctime:', ctime)
	print('cvenue:', cvenue)
	print('cremark:', cremark)

	return (cindex, ctype, cgroup, cday, ctime, cvenue, cremark)

	#cur.execute('''INSERT OR IGNORE INTO Courses (ccode, cname, cau)
    #    VALUES ( ?, ?, ? )''', ( ccode, cname, cau))

def parseIndexTable(table):
	print('==== START PARSING INDEX TABLE ====')
	#print(table)
	indexes = []
	rows = table.find_all(attrs={"bgcolor":"#CAE2EA"})
	print('found:', len(rows), "indexes")
	for row in rows:
		indexes.append(parseIndexRow(row))
	return indexes

	#print(table.contents[3])
	#parseIndexRow(table.contents[3])

#	for i in range (len(table.contents[3])):
#		row = table.contents[3].contents
#		print(i,':', row)
#		if table.contents[3].contents == '\n':
#			counter -=1
#			continue
		
    





baseurl ="https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1"

r = requests.post(baseurl, 
	#data={'staff_access':'false','acadsem':'2018;1', 'r_subj_code':'cz3007', 'boption':'Search', 'r_search_type': 'F'})
	data={'staff_access':'false','acadsem':'2018;1', 'r_subj_code':'cz3007', 'boption':'CLoad', 'r_search_type': 'F', 'r_course_yr':'CSC;;4;F'})
print('status', r.status_code, r.reason)
#print(r.text + '...')

conn = sqlite3.connect('content.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Courses
	(id INTEGER PRIMARY KEY AUTOINCREMENT, ccode TEXT UNIQUE, cname TEXT, 
	cau TEXT)''')

cur.execute('''CREATE TABLE IF NOT EXISTS CourseIndexes
	(id INTEGER PRIMARY KEY AUTOINCREMENT, course_ccode TEXT, cindex TEXT, ctype TEXT, 
	cgroup TEXT, cday TEXT, ctime TEXT, cvenue TEXT, cremark TEXT)''')



soup = BeautifulSoup(r.text, 'html.parser')
#print(soup)
tables = soup.find_all('table')

print ('number of tables: ', len(tables))


for i in range (len(tables)):
	print('')
	print('Table number:', i)
	if i %2 ==0:		
		(ccode, cname, cau) = parseCourse(tables[i])
		cur.execute('''INSERT OR IGNORE INTO Courses (ccode, cname, cau)
        VALUES ( ?, ?, ? )''', ( ccode, cname, cau))

	else:
		indexes = parseIndexTable(tables[i])
		for (cindex, ctype, cgroup, cday, ctime, cvenue, cremark) in indexes:
			cur.execute('''INSERT OR IGNORE INTO CourseIndexes (course_ccode, cindex, ctype, cgroup, cday, ctime, cvenue, cremark)
			 	VALUES ( ?, ?, ?, ?, ?, ?, ?, ?)''', ( ccode, cindex, ctype, cgroup, cday, ctime, cvenue, cremark))


#cindex
#ctype
#cgroup
#day
#ctime
#cremark

conn.commit()
cur.close()



