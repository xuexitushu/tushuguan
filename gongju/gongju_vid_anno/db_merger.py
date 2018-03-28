#db_merger.py
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import FrameAnnotation, LabelClass, LabelState, Project, RawData

# Define and init DBs
db_1 = sys.argv[1]
db_2 = sys.argv[2]
engine_1 = create_engine('sqlite:///' + db_1, convert_unicode=True)
engine_2 = create_engine('sqlite:///' + db_2, convert_unicode=True)
#db_session_1 = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine_1))
db_session_1 = scoped_session(sessionmaker(autocommit=True, autoflush=False, bind=engine_1))
#db_session_2 = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine_2))
db_session_2 = scoped_session(sessionmaker(autocommit=True, autoflush=False, bind=engine_2))
Base1 = declarative_base()
Base2 = declarative_base()
Base1.query = db_session_1.query_property()
Base2.query = db_session_2.query_property()
# Base1.metadata.create_all(bind=engine_1)
# Base2.metadata.create_all(bind=engine_2)


# merge projects
q1 = db_session_1.query(Project).all()
q2 = db_session_2.query(Project).all()
project_merge_map = {}
for e1 in q1:
    entry_exists = False
    for e2 in q2:
        if e1.name == e2.name:
            project_merge_map[e1.id] = e2.id
            entry_exists = True

    if not entry_exists:
        new_e = Project(e1.name)
        db_session_2.add(new_e)
        db_session_2.commit()
        db_session_2.refresh(new_e)
        project_merge_map[e1.id] = new_e.id
        print "merged project entry " + e1.name + " with id " + str(new_e.id)

# Merge Raw Data
rawdata_query1 = db_session_1.query(RawData).all()
rawdata_query2 = db_session_2.query(RawData).all()
rawdata_map = {}
for rde1 in rawdata_query1:
    ex = False
    for rde2 in rawdata_query2:
        if rde1.name == rde2.name:
            rawdata_map[rde1.id] = rde2.id
            ex = True
    if not ex:
        # determine project id
        project_id = project_merge_map[rde1.project_id]
        new_rd = RawData(rde1.name, rde1.project_id)
        db_session_2.add(new_rd)
        db_session_2.commit()
        db_session_2.refresh(new_rd)
        rawdata_map[new_rd.name] = new_rd.id
        print "merged raw data entry " + new_rd.name + " with id " + str(new_rd.id)

# Merge Entries
anno_query1 = db_session_1.query(FrameAnnotation).all()
for anno in anno_query1:
    rd_id = rawdata_map[anno.raw_data_id]
    anno_db2 = db_session_2.query(FrameAnnotation) \
        .filter(FrameAnnotation.raw_data_id == rd_id, FrameAnnotation.frame == anno.frame) \
        .first()

    if anno_db2 is None:
        new_fa = FrameAnnotation(rd_id, anno.frame, anno.frame_name, anno.label_data, anno.last_updated)
        db_session_2.add(new_fa)
        db_session_2.commit()
        db_session_2.refresh(new_fa)
        print "added entry for:" + str(new_fa.frame)



