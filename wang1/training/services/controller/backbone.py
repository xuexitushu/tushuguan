#controller de basebone.py
import config
from log import logger

import json
import os
import random
import db
import requests
import subprocess

from services.backbone_base import Backbone, create_url_from_ip

STATUS_LOST = "Lost"

TRAINER_PREFIX = ""


class BackboneController(Backbone):

    def __init__(self):
        self.db = config.general.local_db
        self.port = config.general.port
        self.mdbshared = config.general.modeldb_shared
        self.data_center_url = create_url_from_ip(config.data_center.ip, config.data_center.port)
        self.db_manager = db.DataBaseManager(self.db)

        for trainer in config.sub_services:
            address = create_url_from_ip(trainer.ip, trainer.port)
            self.db_manager.add_training_node(trainer.name, address)

    def update_sub_service_status(self):
        nodes = self.db_manager.get_all_nodes()
        for n in nodes:
            try:
                req = requests.get(n.address + TRAINER_PREFIX + "/status")
                #logger.debug("status response from trainer: %s ", str(req))
                status = json.loads(req.content)["status"]
                self.db_manager.update_node_status(n.id, status)
            except Exception:
                self.db_manager.update_node_status(n.id, STATUS_LOST)

        self.data_center_status = self.ping_data_center()[self.data_center_url]

    def update_experiment_status(self):
        exp = self.db_manager.get_ongoing_experiments()
        for e in exp:
            if not self.db_manager.get_node_from_id(e.node_id).status == "Idle":
                continue

            data = self.get_experiment_status(e.id)

            if 'error' in data:
                self.db_manager.set_experiment_status(e.id, "Unknown")
            else:
                try:
                    data = data["status"]
                    train_status = data["train_status"]
                    train_job_id = data["train_job_id"]
                    url = data["url"]

                    logger.info("train status: %s", train_status)

                    self.db_manager.set_experiment_status(e.id, train_status)
                    self.db_manager.set_experiment_train_job_id(e.id, train_job_id)
                    self.db_manager.set_experiment_train_url(e.id, url)
                    self.db_manager.set_experiment_results(e.id, data)
                except Exception as err:
                    print "update_experiment_status error: ", err

    def sync_db(self):
        self.update_sub_service_status()
        self.update_experiment_status()

    def ping(self):
        try:
            nodes = self.ping_sub_services()
            datacenter = self.ping_data_center()

            result = {}
            result["nodes"] = nodes
            result["datacenter"] = datacenter
            return result
        except:
            raise

    def ping_sub_services(self):
        try:
            nodes = self.db_manager.get_all_nodes()

            res = {}
            for n in nodes:
                logger.info("ping subservice@:%s", n.name)
                res[n.name] = self.is_sub_service_alive(n.address)
            return res
        except:
            raise

    def ping_data_center(self):
        try:
            #logger.debug("ping_data_center@%s", self.data_center_url)
            res = {}
            res[self.data_center_url] = self.is_sub_service_alive(self.data_center_url)
            return res
        except:
            raise

    def list_available_data(self):
        try:
            logger.info("requesting list from datacenter %s", self.data_center_url)
            response = requests.get(self.data_center_url + "/index.json")
            data = json.loads(response.content)
            return data
        except:
            raise Exception("Cannot reach data center")

    def list_nodes(self):
        try:
            nodes = self.db_manager.get_all_nodes()

            res = {}
            for n in nodes:
                res[n.id] = n.as_dict()
            return res
        except:
            raise

    def queue_experiment(self, node_id, data_job_id, data):
        try:
            node = self.db_manager.get_node_from_id(node_id)

            if not self.is_sub_service_alive(node.address):
                raise IOError("Sub service is dead!")

            if not self.is_sub_service_alive(self.data_center_url):
                raise IOError("Data center is dead!")

            exp_id = self.db_manager.add_experiment(node_id, data_job_id, data)

            res = requests.get(node.address + TRAINER_PREFIX + "/queue/" + str(exp_id) + "/" + data_job_id, data=data).content

            return res
        except Exception as err:
            raise err

    def get_experiment_status(self, exp_id):
        exp = self.db_manager.get_experiment(exp_id)
        try:
            node = self.db_manager.get_node_from_id(exp.node_id)
        except ValueError as e:
            raise e

        res = json.loads(requests.get(node.address + TRAINER_PREFIX + "/exp/" + str(exp_id)).content)
        return res

    def get_experiments_by_project_id(self, proj_id):
        exp = self.db_manager.get_experiments_by_project(proj_id)
        all = []
        for e in exp:
            all.append(e.as_dict())

        try:
            pr = self.db_manager.get_project(proj_id)
        except ValueError as err:
            return "Project not found", all

        return pr.name, all

    def list_projects(self):
        projs = self.db_manager.get_projects()
        all = []
        for p in projs:
            all.append(p.as_dict())
        return all

    def send_exp_to_modeldb(self, eid):
        try:
            exp = self.db_manager.get_experiment(eid)

            modeldb_file = "config/modeldb.json"
            with open(modeldb_file, "r") as f:
                data = json.load(f)

            data["MODEL"]["NAME"] = exp.train_job_uid
            data["MODEL"]["METRICS"][0]["VALUE"] = exp.result.accuracy
            data["MODEL"]["CONFIG"]["learning_rate"] = exp.cls_param.learning_rate
            data["MODEL"]["CONFIG"]["epoch"] = exp.cls_param.train_epochs
            data["MODEL"]["CONFIG"]["train_id"] = exp.train_job_uid
            data["DATASETS"][0]["FILENAME"] = exp.data_job_uid
            data["DATASETS"][0]["METADATA"]["datasetid"] = exp.data_job_uid

            out = json.dumps(data)
            filename = os.path.join(self.mdbshared, "JsonSample.json")

            with open(filename, "w") as f:
                f.write(str(out))

            syncher = "config/syncer.json"
            with open(syncher, "r") as f:
                data = json.load(f)

            data["project"]["name"] = exp.project.name
            data["project"]["description"] = exp.project.desc
            data["experiment"]["name"] = exp.train_job_uid

            out = json.dumps(data)
            filename = os.path.join(self.mdbshared, "syncer.json")

            with open(filename, "w") as f:
                f.write(str(out))

            logfile = open("sender_log", "w")
            error = open("sender_err", "w")
            exp_sender = "config/send_to_mdb.sh"
            pid = subprocess.Popen(["sh", exp_sender], stdout=logfile, stderr=error)
            out, err = pid.communicate()
            print out, err

            # update experiment evaluation status as evaluated
            self.db_manager.set_experiment_eval_status(eid, True)

            return "Experiment "+str(eid)+" has been sent to modeldb server successfully!"
        except Exception as e:
            return "Can't upload experiment to ModelDB server"

    def get_all_experiments(self):
        try:
            exp = self.db_manager.get_all_experiments()
            all = []
            for e in exp:
                all.append(e.as_dict())
        except:
            return "Can't find any"
        return all

    def get_gpu_usage(self):
        try:
            nodes = self.db_manager.get_all_nodes()
            all = []
            for n in nodes:
                res = {}
                res["id"] = n.id
                res["name"] = n.name
                try:
                    response = requests.get(n.address + TRAINER_PREFIX + "/gpu").content
                    res["nvidia-smi"] = response
                except Exception as e:
                    res["error"] = "Can't receive information"
                all.append(res)
            return all
        except:
            raise
