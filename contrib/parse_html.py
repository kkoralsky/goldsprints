#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from urllib import urlopen
import sys
from random import random

if len(sys.argv)>1:
    html_content=open(sys.argv[1]).read()
else:
    html_content=urlopen('http://www.warsawcarkillers.org/index.php/registration/registered-raced/').read()

soup=BeautifulSoup(html_content)

for nr in soup.findAll('strong', attrs={'class': 'racenumber'}):
    try:
        n=int(nr.contents[0])
    except ValueError:
        continue
    names=nr.parent.findNextSibling('td').contents[0].strip().replace('\t\t\t\t', ' ')
    if len(nr.parent.findNextSibling('td').findChild('em').contents)>0:
        names=nr.parent.findNextSibling('td').findChild('em').contents[0][len('a.k.a. '):]
    if random()>.8:
        print n, u'female', names.encode('utf8')
    else:
        print n, u'male', names.encode('utf8')
        
    
