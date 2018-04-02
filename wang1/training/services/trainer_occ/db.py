#db.py
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Float, func, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils.functions import drop_database, create_database
import os
import random
import json
from sqlalchemy import or_, and_

Base = declarative_base()

class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True)
    network_id = Column(Integer, ForeignKey("network_architecture.id"))
    cls_param_id = Column(Integer, ForeignKey("cls_hyper_params.id"))
    node_id = Column(Integer, ForeignKey("training_nodes.id"))
    result_id = Column(Integer, ForeignKey("exp_results.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    train_url = Column(String(512), nullable=True, unique=False)
    data_job_uid = Column(String(512), nullable=True, unique=False)
    train_job_uid = Column(String(512), nullable=True, unique=False)
    status = Column(String(512), nullable=False)
    eval_status = Column(Boolean)
    cls_param = relationship("ClassificationHyperParam", back_populates="experiment")
    arch = relationship("NetworkArchitecture", back_populates="experiment")
    result = relationship("ExperimentResult", back_populates="experiment")
    project = relationship("Project", back_populates="experiment")
    date = Column(DateTime, default=func.now())
    def as_dict(self):
        res = {}
        res["id"] = self.id
        res["status"] = self.status
        res["node_id"] = self.node_id
        res["train_url"] = self.train_url
        return res
    def __init__(self, data_job_uid):
        self.data_job_uid = data_job_uid
        self.status = "Unknown"
        self.loss = -1.0
        self.eval_status = False
    def __repr__(self):
        return "<Experiment id=%s>" % self.id

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    desc = Column(String(512), nullable=True, unique=False)
    experiment = relationship("Experiment", back_populates="project")
    def as_dict(self):
        res = {}
        res['id'] = self.id
        res['name'] = self.name
        res['desc'] = self.desc
        return res
    def __init__(self, name, description=""):
        self.name = name
        self.desc = description
    def __repr__(self):
        return "<Project name=%s>" % self.name

class ClassificationHyperParam(Base):
    __tablename__ = "cls_hyper_params"
    id = Column(Integer, primary_key=True)
    learning_rate = Column(Float)
    train_epochs = Column(Integer)
    experiment = relationship("Experiment", back_populates="cls_param")
    def to_json(self):
        pass
    def __init__(self, learning_rate, train_epochs):
        self.learning_rate = learning_rate
        self.train_epochs = train_epochs
    def __repr__(self):
        return "<ClassificationHyperParam path=%s>" % self.path

class ExperimentResult(Base):
    __tablename__ = "exp_results"
    id = Column(Integer, primary_key=True)
    accuracy = Column(Float)
    epoch = Column(Integer)
    learning_rate = Column(Float)
    loss_train = Column(Float)
    loss_val = Column(Float)
    progress = Column(Integer)
    elapsed = Column(Float)
    experiment = relationship("Experiment", back_populates="result")
    def to_json(self):
        pass
    def __repr__(self):
        return "<ExperimentResult accuracy=%s>" % self.accuracy

class NetworkArchitecture(Base):
    __tablename__ = "network_architecture"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    framework = Column(String(255), nullable=False, unique=False)
    experiment = relationship("Experiment", back_populates="arch")
    def __init__(self, name, framework):
        self.name = name
        self.framework = framework
    def __repr__(self):
        return "<NetworkArchitecture name=%s>" % self.name

class TrainingNode(Base):
    __tablename__ = "training_nodes"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    address = Column(String(255), nullable=False, unique=True)
    status = Column(String(255), nullable=True)
    def __init__(self, name = "", address = ""):
        self.status = "Unknown"
        self.name = name
        self.address = address
    def as_dict(self):
        res = {}
        res['name'] = self.name
        res['address'] = self.address
        res['status'] = self.status
        return res
    def __repr__(self):
        return "<TrainingNode name=%s>" % self.address

class DataBaseManager(object):
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
        # set all node status to unknown
        #session.add(TrainingNode("Local Trainer", "http://127.0.0.1:8001"))
        session.add(NetworkArchitecture("lenet", "caffe"))
        session.add(NetworkArchitecture("googlenet", "caffe"))
        session.add(NetworkArchitecture("alexnet", "caffe"))
        session.commit()
        print "db generation success..."
    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()
    def get_all_nodes(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session.query(TrainingNode).all()
    def update_node_status(self, nid, status):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if not session.query(TrainingNode).filter(TrainingNode.id == nid).count():
            raise ValueError("Wrong TrainingNode ID")
        node = session.query(TrainingNode).filter(TrainingNode.id == nid).all()[0]
        node.status = status
        session.add(node)
        session.commit()
    def add_experiment(self, nid, data_job_uid, data):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if not session.query(TrainingNode).filter(TrainingNode.id == nid).count():
            raise ValueError("Wrong TrainingNode id")
        params = json.loads(data)
        p = ClassificationHyperParam(params["learning_rate"], params["train_epochs"])
        session.add(p)
        session.commit()
        try:
            n = session.query(NetworkArchitecture).filter(NetworkArchitecture.name == params["standard_networks"]).all()[0]
        except Exception as err:
            raise err
        r = ExperimentResult()
        try:
            proj = session.query(Project).filter(Project.name == params["project"]).all()[0]
        except Exception as err:
            proj = Project(params["project"])
        e = Experiment(data_job_uid)
        e.arch = n
        e.cls_param = p
        e.node_id = nid
        e.result = r
        e.project = proj
        session.add(e)
        session.commit()
        return e.id
    def get_node_from_id(self, nid):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        nodes = session.query(TrainingNode).filter(TrainingNode.id == nid).all()
        if not len(nodes):
            raise ValueError("There is no TrainingNode with given id")
        return nodes[0]
    def get_experiment(self, eid):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        exp = session.query(Experiment).filter(Experiment.id == eid).all()
        if not len(exp):
            raise ValueError("There is no exp with given id")
        return exp[0]
    def get_all_experiment_wo_train_job_id(self, eid):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        exp = session.query(Experiment).filter(Experiment.train_job_uid.is_(None)).all()
        if not len(exp):
            raise ValueError("There is no exp with given id")
        return exp[0]
    def get_ongoing_experiments(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        exp = session.query(Experiment).filter(and_(Experiment.status.isnot("Failed"),
                                                    Experiment.status.isnot("Error"),
                                                    Experiment.status.isnot("Done"),
                                                    Experiment.status.isnot("Aborted")
                                                    )).all()
        return exp
    def set_experiment_status(self, eid, status):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if not session.query(Experiment).filter(Experiment.id == eid).count():
            raise ValueError("Wrong experiment id")
        exp = session.query(Experiment).filter(Experiment.id == eid).all()[0]
        exp.status = status
        session.add(exp)
        session.commit()
    def set_experiment_train_job_id(self, eid, train_job_id):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if not session.query(Experiment).filter(Experiment.id == eid).count():
            raise ValueError("Wrong experiment id")
        exp = session.query(Experiment).filter(Experiment.id == eid).all()[0]
        exp.train_job_uid = train_job_id
        session.add(exp)
        session.commit()
    def set_experiment_train_url(self, eid, train_url):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if not session.query(Experiment).filter(Experiment.id == eid).count():
            raise ValueError("Wrong experiment id")
        exp = session.query(Experiment).filter(Experiment.id == eid).all()[0]
        exp.train_url = train_url
        session.add(exp)
        session.commit()
    def set_experiment_results(self, eid, data):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if not session.query(Experiment).filter(Experiment.id == eid).count():
            raise ValueError("Wrong experiment id")
        exp = session.query(Experiment).filter(Experiment.id == eid).all()[0]
        #print "DB: ", data
        try:
            exp.result.accuracy = data["accuracy"]
            exp.result.elapsed = data["elapsed"]
            exp.result.epoch = data["epoch"]
            exp.result.loss_train = data["loss_train"]
            exp.result.loss_val = data["loss_val"]
            exp.result.progress = data["progress"]
            exp.result.learning_rate = data["learning_rate"]
            session.add(exp)
            session.commit()
        except Exception as err:
            print "Error@set_experiment_results", err
            raise err
    def get_experiments_by_project(self, proj_id):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        exp = session.query(Experiment).filter(Experiment.project_id.is_(proj_id)).all()
        return exp
    def get_projects(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        proj = session.query(Project).all()
        return proj
    def set_experiment_eval_status(self, eid, status):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if not session.query(Experiment).filter(Experiment.id == eid).count():
            raise ValueError("Wrong experiment id")
        exp = session.query(Experiment).filter(Experiment.id == eid).all()[0]
        exp.eval_status = status
        session.add(exp)
        session.commit()
    def get_project(self, pid):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if not session.query(Project).filter(Project.id == pid).count():
            raise ValueError("Wrong project id")
        pr = session.query(Project).filter(Project.id.is_(pid)).all()[0]
        return pr
    def get_all_experiments(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        exp = session.query(Experiment).all()
        return exp
    def add_training_node(self, name, address):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if session.query(TrainingNode).filter(TrainingNode.name == name,
                                              TrainingNode.address == address).count():
            return
        session.add(TrainingNode(name, address))
session.commit()
