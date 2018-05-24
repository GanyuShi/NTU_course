from urllib.parse import urlencode
from urllib.request import Request, urlopen
import sqlite3
from bs4 import BeautifulSoup
import time
import ssl


def parseCourse(table):
	#print("==== START PARSING COURSE TABLE ====")
	global ccode
	ccode = table.find_all(attrs={"width": "100"})[0].string.strip()
	cname = table.find_all(attrs={"width": "500"})[0].string.strip()
	cau = table.find_all(attrs={"width": "50"})[0].string.strip()
	#print ('course code:', ccode)
	#print ('course name:', cname)
	#print ('course AU:', cau)

	return (ccode, cname, cau)


def parseIndexRow(row):
	#print("==== START PARSING INDEX ROW ====")
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

	#print('cindex:', cindex)
	#print('ctype:', ctype)
	#print('cgroup:', cgroup)
	#print('cday:', cday)
	#print('ctime:', ctime)
	#print('cvenue:', cvenue)
	#print('cremark:', cremark)

	return (cindex, ctype, cgroup, cday, ctime, cvenue, cremark)

def parseIndexTable(table):
	#print('==== START PARSING INDEX TABLE ====')
	indexes = []
	rows = table.find_all(attrs={"bgcolor":"#CAE2EA"})
	#print('found:', len(rows), "indexes")
	for row in rows:
		indexes.append(parseIndexRow(row))
	return indexes


conn = sqlite3.connect('content.sqlite')
cur = conn.cursor()


# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

baseurl = input ('Enter URL: ')

if len(baseurl) < 1:
    baseurl = "https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1"

baseurl ="https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1"



cur.execute('''CREATE TABLE IF NOT EXISTS Courses
	(id INTEGER PRIMARY KEY AUTOINCREMENT, ccode TEXT UNIQUE, cname TEXT,
	cau TEXT)''')

cur.execute('''CREATE TABLE IF NOT EXISTS CourseIndexes
	(id INTEGER PRIMARY KEY AUTOINCREMENT, course_ccode TEXT, cindex TEXT, ctype TEXT,
	cgroup TEXT, cday TEXT, ctime TEXT, cvenue TEXT, cremark TEXT)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Fetch
	(id INTEGER PRIMARY KEY AUTOINCREMENT, courseYr_id INTEGER, fetched BOOLEAN DEFAULT FALSE)''')

r_course_yrs = cur.execute('''SELECT * FROM CourseYrs
              WHERE id Not IN (SELECT courseYr_id FROM Fetch)''')

count = 0
for row in r_course_yrs.fetchall():

    print('==== Number', count, "====")
    r_course_yr = row[2]
    print('course yr:', r_course_yr)

    if r_course_yr is None:
        break


    post_fields = {'staff_access': 'false', 'acadsem': '2018;1', 'boption': 'CLoad', 'r_search_type': 'F',
            'r_course_yr': r_course_yr}

    url = Request(baseurl, urlencode(post_fields).encode())

    html = "None"
    try:
        # Open with a timeout of 30 seconds
        document = urlopen(url, None, 30, context=ctx)
        html = document.read().decode()
        if document.getcode() != 200:
            print("Error code=", document.getcode(), url)
            break
    except KeyboardInterrupt:
        conn.commit()
        cur.close()
        print('')
        print('Program interrupted by user...')
        break
    except Exception as e:
        conn.commit()
        cur.close()
        print("Unable to retrieve or parse page", url)
        print("Error", e)
        fail = fail + 1
        if fail > 5: break
        continue

    count += 1

    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')

    print ('number of tables: ', len(tables))


    for i in range (len(tables)):
        #print('')
        #print('Table number:', i)
        if i %2 ==0:
            (ccode, cname, cau) = parseCourse(tables[i])
            cur.execute('''INSERT OR IGNORE INTO Courses (ccode, cname, cau)
            VALUES ( ?, ?, ? )''', ( ccode, cname, cau))

        else:
            indexes = parseIndexTable(tables[i])
            for (cindex, ctype, cgroup, cday, ctime, cvenue, cremark) in indexes:
                cur.execute('''INSERT OR IGNORE INTO CourseIndexes (course_ccode, cindex, ctype, cgroup, cday, ctime, cvenue, cremark)
                    VALUES ( ?, ?, ?, ?, ?, ?, ?, ?)''', ( ccode, cindex, ctype, cgroup, cday, ctime, cvenue, cremark))
    cur.execute('''INSERT OR IGNORE INTO Fetch (courseYr_id, fetched) VALUES (?, ?)''', (row[0], True) )


    if count % 50 == 0: conn.commit()
    if count % 100 == 0: time.sleep(1)
conn.commit()
time.sleep(1)
cur.close()


