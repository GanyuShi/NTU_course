from bs4 import BeautifulSoup
import ssl
import requests
import sqlite3

def parseRow(row):
	#print(row)
	tds = row.find_all('td')
	
	if len(tds) != 7:
		return
	for td in tds:
		if td.string is None:
			return
	
	date = tds[0].string.strip()
	day = tds[1].string.strip()
	time = tds[2].string.strip()
	course = tds[3].string.strip()
	courseTitle = tds[4].string.strip()
	duration = tds[5].string.strip()
	venue = tds[6].string.strip()

	return (date, day, time, course, courseTitle, duration, venue)


conn = sqlite3.connect('content.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Exams
	(id INTEGER PRIMARY KEY AUTOINCREMENT,
	edate TEXT, 
	eday TEXT,
	etime TEXT,
	ecourse TEXT UNIQUE,
	ecourseTitle TEXT,
	eduration TEXT,
	evenue TEXT)''')


baseurl ="https://wis.ntu.edu.sg/webexe/owa/exam_timetable_und.get_detail"

r = requests.post(baseurl, 
	#data={'staff_access':'false','acadsem':'2018;1', 'r_subj_code':'cz3007', 'boption':'Search', 'r_search_type': 'F'})
	data={
	'p_exam_dt':'',
	'p_start_time':'',
	'p_dept':'',
	'p_subj':'',
	'p_venue':'',
	'p_matric':'',
	'academic_session':'Semester 2 Academic Year 2017-2018',
	'p_plan_no':'2',
	'p_exam_yr':'2017',
	'p_semester':'2',
	'bOption':'Next',})

print('status', r.status_code, r.reason)

soup = BeautifulSoup(r.text, 'html.parser')
#print (soup)
table = soup.find_all('table')[2]
rows = table.find_all('tr')
print(len(rows))
for row in rows:
	result = parseRow(row)
	if  result is None:
		continue
	print('')
	(date, day, time, course, courseTitle, duration, venue) = result
	print ('date:', date)
	print ('day:', day)
	print ('time:', time)
	print ('course:', course)
	print ('courseTitle:', courseTitle)
	print ('duration:', duration)
	print ('venue:', venue)

	cur.execute('''
	INSERT OR IGNORE INTO Exams (edate, eday, etime, ecourse, ecourseTitle, eduration, evenue)
	VALUES ( ?, ?, ?, ?, ?, ?, ?)''', (date, day, time, course, courseTitle, duration, venue))
conn.commit()
cur.close()
