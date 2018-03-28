#export_service.py
import os
import re
import encodings
import string
from .. db_service import DBService

print "---Exporting---"

service = DBService()
rows = service.export_nrplatecsv()
print "---number of entries: "+str(len(rows)-1) +" ---"
export_rows = []
header = "folder,image,rows,numberplate,country,comment"
export_rows.append(header)
for row in rows:
    split = string.split(row,',')
    nrs = split[3]
    cmt = "null"
    nrs_split = nrs.split('#')
    if len(nrs_split) > 1:
        nrs = nrs_split[0].strip('\n').strip()
        cmt = nrs_split[1]
        cmt = cmt.strip('\n').replace(';',' ')
    frow = split[0]+","+split[1]+","+split[2]+","+nrs+","+split[4].strip()+","+cmt
    export_rows.append(frow.encode('utf-8').strip())


filename = "export/export2.csv"
if not os.path.exists(os.path.dirname(filename)):
    os.makedirs(os.path.dirname(filename))
with open(filename,'w') as f:
    f.write('\n'.join(export_rows))
    f.close




