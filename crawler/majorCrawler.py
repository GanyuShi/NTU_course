from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import sqlite3

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


conn = sqlite3.connect('content.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS CourseYrs
	(id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT, 
	value TEXT UNIQUE)''')


url = input('Enter - ')
if len(url) < 1:
	url = "http://wish.wis.ntu.edu.sg/webexe/owa/aus_schedule.main"

html = urlopen(url, context=ctx).read()

soup = BeautifulSoup(html, "html.parser")

# Retrieve select course year tag
selectCourseYear = soup.find_all('select', attrs = {'name' : 'r_course_yr'})[0]

# Retrieve all select course year option tags
courseYears = selectCourseYear.find_all('option')
for courseYear in courseYears:
	if courseYear.get('value',None).strip() == (None or ''):
		continue
	name = courseYear.string
	value = courseYear['value']
	print('name:', name)
	print('value:', value)

	cur.execute('''INSERT OR IGNORE INTO CourseYrs (name, value)
        VALUES ( ?, ?)''', ( name, value))
conn.commit()
cur.close()