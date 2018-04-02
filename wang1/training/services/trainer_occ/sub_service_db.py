#sub_service_db.py
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils.functions import drop_database, create_database
import sqlalchemy
import os
import random
import json
from log import logger
Base = declarative_base()

class Experiment(Base):
    __tablename__ = "experiments_occ"
    id = Column(Integer, primary_key=True)
    data_status = Column(String(512), nullable=False)
    train_status = Column(String(512), nullable=False)
    exp_id = Column(Integer, unique=True, nullable=False)
    data_job_id = Column(String(512), nullable=False)
    train_job_id = Column(String(512), nullable=True, unique=True)
    param_path = Column(String(512), nullable=False, unique=True)
    accuracy = Column(Float)
    epoch = Column(Integer)
    learning_rate = Column(Float)
    loss_train = Column(Float)
    loss_val = Column(Float)
    progress = Column(Integer)
    elapsed = Column(Float)
    def __init__(self, exp_id, data_job_id, param_path):
        self.exp_id = exp_id
        self.data_job_id = data_job_id
        self.param_path = param_path
        self.data_status = "Unknown"
        self.train_status = "Unknown"
        self.accuracy = -1.0
        self.epoch = 0
        self.learning_rate = 0.0
        self.loss_train = -1.0
        self.loss_val = -1.0
        self.progress = 0
        self.elapsed = 0.0
    def __repr__(self):
        return "<Experiment id=%s>" % self.id

class DataBaseManagerSubService(object):
    def __init__(self, local_db_name):
        self.url = "sqlite:///" + local_db_name
        print "creating db @:", self.url
        self.engine = create_engine(self.url, isolation_level="READ UNCOMMITTED", echo=False)
        if not os.path.exists(local_db_name):
            self.reset()
    def reset(self):
        try:
            drop_database(self.url)
        except:
            pass
        create_database(self.url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.commit()
        print "db generation success..."
    def create_uid_for_params(self, exp_id, data_job_uid):
        return "/tmp/" + str(exp_id) + "_" + data_job_uid + ".json"
    def add_experiment(self, exp_id, data_job_uid, data):
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            path = self.create_uid_for_params(exp_id, data_job_uid)
            logger.info("Saved file: %s", path)
            logger.info("data at db.add_experiment: %s", data)
            with open(path, 'w') as fp:
                json.dump(data, fp)
            logger.info("params saved to %s", path)
            e = Experiment(exp_id, data_job_uid, path)
            logger.info("experiment object %s", e)
            session.add(e)
            session.commit()
            logger.info("Local experiment generated (eid): ", e.id)
            return e.id
        except Exception as err:
            raise err
    def set_experiment_data_status(self, eid, status):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if not session.query(Experiment).filter(Experiment.id == eid).count():
            raise ValueError("Wrong experiment id")
        exp = session.query(Experiment).filter(Experiment.id == eid).all()[0]
        exp.data_status = status
        session.add(exp)
        session.commit()
    def set_experiment_train_status(self, eid, status):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if not session.query(Experiment).filter(Experiment.id == eid).count():
            raise ValueError("Wrong experiment id")
        exp = session.query(Experiment).filter(Experiment.id == eid).all()[0]
        exp.train_status = status
        session.add(exp)
        session.commit()

    def set_experiment_train_job_id(self, eid, job_id):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if not session.query(Experiment).filter(Experiment.id == eid).count():
            raise ValueError("Wrong experiment id")
        exp = session.query(Experiment).filter(Experiment.id == eid).all()[0]
        exp.train_job_id = job_id
        session.add(exp)
        session.commit()
    def get_experiments_in_progress(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        exp = session.query(Experiment).filter(Experiment.data_status == "In Progress").all()
        if not len(exp):
            raise ValueError("There is no exp with given id")
        return exp
    def get_experiments_waiting(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        exp = session.query(Experiment).filter(Experiment.data_status == "Waiting").all()
        if not len(exp):
            raise ValueError("There is no exp with given id")
        return exp
    def set_dangling_experiments_as_failed(self):
        try:
            eprog = self.get_experiments_in_progress()
            for e in eprog:
                self.set_experiment_data_status(e.id, "Failed")
        except:
            pass
        try:
            ewait = self.get_experiments_waiting()
            for e in ewait:
                self.set_experiment_data_status(e.id, "Failed")
        except:
            pass
    def get_experiment(self, eid):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        exp = session.query(Experiment).filter(Experiment.id == eid).all()
        if not len(exp):
            raise ValueError("There is no exp with given id")
        return exp[0]
    def get_experiment_global(self, eid):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        exp = session.query(Experiment).filter(Experiment.exp_id == eid).all()
        if not len(exp):
            raise ValueError("There is no exp with given id")
        return exp[0]
    def is_exp_in_progress(self, eid):
        return self.get_experiment(eid).data_status == "In Progress"
    def get_experiments_with_train_job_id(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        exp = session.query(Experiment).filter(Experiment.train_job_id.isnot(None)).all()
        return exp
    def set_experiment_results(self, data):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        train_job_id = data["id"]
        if not session.query(Experiment).filter(Experiment.train_job_id == train_job_id).count():
            raise ValueError("Wrong train job id. There is no exp with this id.")
        exp = session.query(Experiment).filter(Experiment.train_job_id == train_job_id).all()[0]
        exp.accuracy = data["accuracy (val) last"]
        exp.elapsed = data["elapsed"]
        exp.epoch = data["epoch (train) last"]
        exp.loss_train = data["loss (train) last"]
        exp.loss_val = data["loss (val) last"]
        exp.progress = data["progress"]
        exp.learning_rate = data["learning_rate (train) last"]
        session.add(exp)
        session.commit()



