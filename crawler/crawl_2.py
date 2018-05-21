from urllib.parse import urlencode
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import ssl
import re

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = input ('Enter URL: ')

if len(url) < 1: 
	url = "https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1"

post_fields = {'staff_access':'false','acadsem':'2018;1', 'r_subj_code':'cz3007', 'boption':'Search', 'r_search_type': 'F'}

#r=requests.post("https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1", 
#data = {'staff_access':'false','acadsem':'2017;1', 'r_subj_code':'cz3007', 'boption':'Search'})

req = Request(url, urlencode(post_fields).encode())

html = urlopen(req).read().decode()

print(html)
#tags = soup('a')
#url = tags[position-1].get('href', None)
#print("position", position, url )