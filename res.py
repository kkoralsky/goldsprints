import csv
import re
from pprint import pprint
l=sorted(csv.reader(open('results.txt')))

f=open('/home/karol/goldsprints_result.txt').readlines()
res=[]
for r in f:
    r=list(re.match(r'(.+)\s+([0-9.]+)', r).groups())
    res.append([r[1],r[0].strip()])

for i,n in enumerate(res):
    for r in l:
        if r[2]==n[1]:
            try: res[i]=[i+1, res[i][0], r[6],r[8],r[3],r[5],r[7],r[4]]
            except IndexError: res[i]=[i+1, res[i][0],'','','',res[i][1],'','']
            break
    else:
        print n

pprint(res)
csv.writer(open('next_res.csv', 'w')).writerows(res)
