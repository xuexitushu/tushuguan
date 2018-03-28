#model.py
import datetime
from sqlalchemy import Column, Integer, String, DateTime
from database import Base


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Project %r>' % (self.name)


class RawData(Base):
    __tablename__ = 'raw_data'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    name = Column(String(50), unique=True)

    def __init__(self, name=None, project_id=None):
        self.name = name
        self.project_id = project_id

    def __repr__(self):
        return '<RawData %r>' % (self.name)


class LabelClass(Base):
    __tablename__ = 'label_class'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    name = Column(String(50))

    def __init__(self, name=None,project_id=None):
        self.name = name
        self.project_id = project_id

    def __repr__(self):
        return '<label_class %r>' % (self.name)


class LabelState(Base):
    __tablename__ = 'label_state'
    id = Column(Integer, primary_key=True)
    label_class_id = Column(Integer)
    name = Column(String(50))

    def __init__(self, name=None, label_class_id=None):
        self.name = name
        self.label_class_id = label_class_id

    def __repr__(self):
        return '<label_state %r>' % (self.name)


class FrameAnnotation(Base):
    __tablename__ = 'frame_annotation'
    raw_data_id = Column(Integer,primary_key=True)
    frame = Column(Integer,primary_key=True)
    frame_name = Column(String)
    label_data = Column(String)
    last_updated = Column(DateTime)
    

    def __init__(self, raw_data_id=None, frame = None, frame_name = None,label_data=None,last_updated = None):
        self.raw_data_id = raw_data_id
        self.frame = frame
        self.frame_name = frame_name
        self.label_data = label_data
        self.last_updated = last_updated