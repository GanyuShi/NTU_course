import sqlite3
import re

conn_o = sqlite3.connect('./../crawlers/content.sqlite')
cur_o =conn_o.cursor()

conn_n = sqlite3.connect('model.sqlite')
cur_n = conn_n.cursor()

cur_n.execute('''DROP TABLE IF EXISTS Indexes''')
cur_n.execute('''DROP TABLE IF EXISTS Lessons''')

cur_n.execute('''CREATE TABLE IF NOT EXISTS Indexes
      (id INTEGER PRIMARY KEY AUTOINCREMENT,
      indexNo INTEGER,
      course_id INTEGER,
      UNIQUE (indexNo, course_id),
      FOREIGN KEY (course_id) REFERENCES Courses(id))''')

cur_n.execute('''CREATE TABLE IF NOT EXISTS Lessons
      (id INTEGER PRIMARY KEY AUTOINCREMENT,
      index_id INTEGER,
      type_id INTEGER,
      group_id INTEGER,
      day_id INTEGER,
      slot_id INTEGER,
      Venue_id INTEGER,
      FOREIGN KEY (index_id) REFERENCES Indexes(id),
      FOREIGN KEY (type_id) REFERENCES LessonTypes(id),
      FOREIGN KEY (group_id) REFERENCES Groups(id),
      FOREIGN KEY (day_id) REFERENCES days(id),
      FOREIGN KEY (slot_id) REFERENCES TimeSlots(id),
      FOREIGN KEY (venue_id) REFERENCES Venues(id),
      UNIQUE (index_id, day_id, slot_id, Venue_id))''')

indexes = cur_o.execute('''SELECT DISTINCT cindex FROM CourseIndexes''').fetchall()

count = 0


def getTypeId(type):
    type = type.strip()
    if type is None or type == '':
        type_id = cur_n.execute('''SELECT id FROM LessonTypes WHERE name = (?)''', ('ONLINE COURSE',)).fetchone()[0]
    else:
        type_id = cur_n.execute('''SELECT id FROM LessonTypes WHERE name = (?)''', (type,)).fetchone()[0]
    return type_id


def getDayId(day):
    day = day.strip()
    if day is None or day == '':
        return None
    day_id = cur_n.execute('''SELECT id FROM Days WHERE name = (?)''', (day,)).fetchone()[0]
    return day_id


def getSlotId(slot):
    slot = slot.strip()
    if slot is None or slot == '':
        return None
    startTime = re.findall('([0-9]*)-', slot)[0]
    startTime = startTime[:2] + ':' + startTime[2:]
    endTime = re.findall('-([0-9]*)', slot)[0]
    endTime = endTime[:2] + ':' + endTime[2:]
    slot_id = cur_n.execute('''SELECT id FROM TimeSlots WHERE startTime = (?) AND endTime = (?)''', (startTime, endTime)).fetchone()[0]
    return slot_id


def getVenueId(venue):
    venue = venue.strip()
    if venue is None or venue == '':
        return None
    venue_id = cur_n.execute('''SELECT id FROM Venues WHERE name = (?)''', (venue,)).fetchone()[0]
    return venue_id


def getGroupId(group):
    group = group.strip()
    if group is None or group == '':
        return None
    group_id = cur_n.execute('''SELECT id FROM Groups WHERE name = (?)''', (group,)).fetchone()[0]
    return group_id


try:
    for index in indexes:
        index = index[0]
        lessons = cur_o.execute('''SELECT * FROM CourseIndexes WHERE cindex = (?)''', (index, )).fetchall()

        for (id, ccode, indexNo, type, group, day, time, venue, remark) in lessons:
            print(id, ccode, indexNo, type, group, day, time, venue, remark)
            course_id = cur_n.execute('''SELECT id FROM Courses WHERE ccode = (?)''', (ccode,)).fetchone()[0]
            indexNo = int(indexNo)
            cur_n.execute('''INSERT OR IGNORE INTO Indexes(course_id, indexNo) VALUES (?, ?)''', (course_id, indexNo))
            index_id = cur_n.execute('''SELECT id FROM Indexes WHERE course_id = (?) AND indexNo = (?)''', (course_id, indexNo)).fetchone()[0]
            type_id = getTypeId(type)
            group_id = getGroupId(group)
            day_id = getDayId(day)
            slot_id = getSlotId(time)
            venue_id = getVenueId(venue)
            print(index_id, type_id, group_id, day_id, slot_id, venue_id)
            cur_n.execute('''INSERT OR IGNORE INTO Lessons(index_id, type_id, group_id, day_id, slot_id, venue_id) VALUES (?,?,?,?,?,?)''',
                          (index_id, type_id, group_id, day_id, slot_id, venue_id))
        count = count +1
        if count % 50 == 0: conn_n.commit()
except KeyboardInterrupt:
    conn_n.commit()
    conn_o.commit()
    cur_n.close()
    cur_o.close()
    print('Interrupt by user')
conn_n.commit()
conn_o.commit()
cur_n.close()
cur_o.close()

