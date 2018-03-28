import sqlite3
db = sqlite3.connect('annotations.db')
c = db.cursor()
def create_table():
  c.execute('CREATE TABLE IF NOT EXISTS frame_annotation (id INTEGER NOT NULL,raw_data_id INTEGER,frame INTEGER,frame_name VARCHAR,label_data VARCHAR,last_updated DATETIME,PRIMARY KEY(id))'),
  c.execute('CREATE TABLE IF NOT EXISTS label_class (id INTEGER NOT NULL,project_id INTEGER,name VARCHAR(50),PRIMARY KEY(id))'),
  c.execute('CREATE TABLE IF NOT EXISTS raw_data (id INTEGER NOT NULL,project_id INTEGER,name VARCHAR(50),PRIMARY KEY(id),UNIQUE(name))'),
  c.execute('CREATE TABLE IF NOT EXISTS project (id INTEGER NOT NULL,name VARCHAR(50),PRIMARY KEY(id),UNIQUE(name))')

def data_entry():
  c.execute("INSERT INTO label_class VALUES(1,1,'object')")
  c.execute("INSERT INTO raw_data VALUES(1,1,'raw')")
  c.execute("INSERT INTO project VALUES(2,'tmp2')")
  db.commit()
  c.close()
  db.close()

create_table()
data_entry()

'''
indexsqlite_autoindex_raw_data_1raw_data
'''