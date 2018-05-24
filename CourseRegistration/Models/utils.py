import sqlite3
import re

conn = sqlite3.connect('model.sqlite')
cur= conn.cursor()

conn_o = sqlite3.connect('./../crawlers/content.sqlite')
cur_o =conn_o.cursor()

cur.execute('''DROP TABLE IF EXISTS Days''')
cur.execute('''DROP TABLE IF EXISTS Venues''')
cur.execute('''DROP TABLE IF EXISTS LessonTypes''')
cur.execute('''DROP TABLE IF EXISTS TimeSlots''')
cur.execute('''DROP TABLE IF EXISTS Groups''')

cur.execute('''CREATE TABLE IF NOT EXISTS Days
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Venues
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT)''')

cur.execute('''CREATE TABLE IF NOT EXISTS LessonTypes
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT)''')

cur.execute('''CREATE TABLE IF NOT EXISTS TimeSlots
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            startTime TIME,
            endTime TIME)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Groups
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT)''')

lessonTypes = cur_o.execute('''SELECT DISTINCT ctype from CourseIndexes''').fetchall()
for lessonType in lessonTypes:
    if (lessonType[0].strip() == ''):
        lessonType = ('ONLINE COURSE',)
    print(lessonType)
    cur.execute('''INSERT INTO LessonTypes(name) values (?) ''', lessonType)

days = cur_o.execute('''SELECT DISTINCT cday from CourseIndexes''').fetchall()
for day in days:
    if (day[0].strip() == ''):
        continue
    print(day)
    cur.execute('''INSERT INTO Days(name) values (?) ''', day)


slots = cur_o.execute('''SELECT DISTINCT ctime FROM CourseIndexes''').fetchall()
for slot in slots:
    slot = slot[0]
    print(slot)
    if slot.strip()=='':
        continue
    startTime = re.findall('([0-9]*)-', slot)[0]
    startTime = startTime[:2] + ':' + startTime[2:]
    endTime = re.findall('-([0-9]*)', slot)[0]
    endTime = endTime[:2] + ':' + endTime[2:]
    print(startTime)
    print(endTime)
    cur.execute('''INSERT INTO TimeSlots(startTime, endTime) VALUES (?,?)''', (startTime, endTime))


venues = cur_o.execute('''SELECT DISTINCT cvenue FROM CourseIndexes''').fetchall()
for venue in venues:
    if (venue[0].strip() ==''):
        continue
    cur.execute('''INSERT INTO Venues(name) VALUES (?)''', venue)


groups = cur_o.execute('''SELECT DISTINCT cgroup FROM CourseIndexes''').fetchall()
for group in groups:
    if (group[0].strip() ==''):
        continue
    cur.execute('''INSERT INTO Groups(name) VALUES (?)''', group)

conn.commit()
cur.close()