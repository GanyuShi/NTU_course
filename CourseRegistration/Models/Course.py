import sqlite3
import re

conn_o = sqlite3.connect('./../crawlers/content.sqlite')
cur_o =conn_o.cursor()

conn_n = sqlite3.connect('model.sqlite')
cur_n = conn_n.cursor()

cur_n.execute('''DROP TABLE IF EXISTS Courses''')
cur_n.execute('''DROP TABLE IF EXISTS UECourses''')
cur_n.execute('''DROP TABLE IF EXISTS SelfPacedCourses''')
cur_n.execute('''DROP TABLE IF EXISTS GerPECourses''')

cur_n.execute('''CREATE TABLE IF NOT EXISTS Courses
      (id INTEGER PRIMARY KEY AUTOINCREMENT,
      ccode TEXT UNIQUE,
      cname TEXT,
      cau INTEGER)''')

cur_n.execute('''CREATE TABLE IF NOT EXISTS UECourses
      (Course_id INTEGER PRIMARY KEY)''')

cur_n.execute('''CREATE TABLE IF NOT EXISTS SelfPacedCourses
      (Course_id INTEGER PRIMARY KEY)''')

cur_n.execute('''CREATE TABLE IF NOT EXISTS GerPECourses
      (Course_id INTEGER PRIMARY KEY)''')

courses = cur_o.execute('''SELECT * FROM Courses''')

count = 0
for (id, ccode, cname, cau) in courses:
    print('==== Number', count, '=====')
    cname = cname.lower()
    specials = re.findall('[*^#]', cname)
    cname = re.sub('[*^#]', '', cname)

    cau = re.findall('([0-9]*\.0)', cau)[0]
    if cau =='':
        cau = 0
    cau = int(float(cau))
    cur_n.execute('''INSERT OR IGNORE INTO Courses (ccode, cname, cau) VALUES (?,?,?)''', (ccode, cname, cau))

    id = cur_n.execute('''SELECT id from Courses WHERE ccode = (?)''', (ccode,)).fetchone()[0]
    print(id, ccode, cname, cau, specials)

    for special in specials:
        if special == '*':
            cur_n.execute('''INSERT OR IGNORE INTO UECourses(Course_id) values (?)''', (id,))
            cname = cname.replace('*','')
            print("Insert into UE Courses")
        elif special == '^':
            cur_n.execute('''INSERT OR IGNORE INTO SelfPacedCourses(Course_id) values (?)''', (id,))
            cname = cname.replace('^','')
            print("Insert into self paced Courses")
        elif special == '#':
            cur_n.execute('''INSERT OR IGNORE INTO GerPeCourses(Course_id) values (?)''', (id,))
            cname = cname.replace('#','')
            print("Insert into GERPE Courses")


    count = count +1
    if count % 100 == 0: conn_n.commit()


conn_n.commit()
conn_o.commit()
cur_n.close()
cur_o.close()
