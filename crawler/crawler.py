import requests
import sqlite3
from bs4 import BeautifulSoup
import re


def parseCourse(table):
	print("==== START PARSING COURSE TABLE ====")
	print(table)

def parseCourseIndex(table):
	print('parse index table')
	print(table)


baseurl ="https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1"

r = requests.post(baseurl, 
	#data={'staff_access':'false','acadsem':'2018;1', 'r_subj_code':'cz3007', 'boption':'Search', 'r_search_type': 'F'})
	data={'staff_access':'false','acadsem':'2018;1', 'r_subj_code':'cz3007', 'boption':'CLoad', 'r_search_type': 'F', 'r_course_yr':'CSC;;4;F'})
print(r.status_code, r.reason)
#print(r.text + '...')

conn = sqlite3.connect('content.sqlite')
cur = conn.cursor()


cur.execute('''CREATE TABLE IF NOT EXISTS Courses
	(id INTEGER UNIQUE, cindex TEXT, ctype TEXT, 
	cgroup TEXT, cday TEXT, ctime TEXT, cremark TEXT)''')


soup = BeautifulSoup(r.text, 'html.parser')
#print(soup)
tables = soup.find_all('table')

print ('number of tables: ', len(tables))
for i in range (len(tables)):
	if i % 2 == 0:		
		parseCourse(tables[i])
	#else:
		#parseCourseIndex(tables[i])

#cindex
#ctype
#cgroup
#day
#ctime
#cremark

conn.commit()
cur.close()



