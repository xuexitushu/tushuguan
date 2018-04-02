#'trainer_occ
#backbone.py
import json
import os
import subprocess
import config
import requests
import subservice_db
import subservice_scheduler
import task_runner
from services.backbone_base import Backbone, create_url_from_ip
from log import logger
# Service status constants
STATUS_IDLE = "Idle"
# Train job constants
JOB_INIT = "Idle"

class BackboneTrainer(Backbone):
    def __init__(self):
        try:
            self.db = config.general.local_db
            self.port = config.general.port
            self.cache = config.general.cache
            # this is address of digits. digits has its own rest service
            self.trainer_url = create_url_from_ip(config.general.trainer_ip, config.general.trainer_port)
        except ValueError as e:
            raise e
        self.service_status = STATUS_IDLE
        self.db_manager = subservice_db.DataBaseManagerSubService(self.db)
        self.task_runner = task_runner.TaskRunner(self.db_manager)
        self.job_scheduler = subservice_scheduler.SubServiceScheduler(self.task_runner)
        self.db_manager.set_dangling_experiments_as_failed()
    def sync_db(self):
        try:
            #todo:customize
            #this is a digits specific request, it keeps digits service up to date
            requests.get(self.trainer_url + '/mobility')
            exps = self.db_manager.get_experiments_with_train_job_id()
            for e in exps:
                data = json.loads(requests.get(self.trainer_url + '/models/' + e.train_job_id + '.json').content)
                if 'error' in data:
                    continue
                status = data["status"]
                self.db_manager.set_experiment_train_status(e.id, status)
            data = json.loads(requests.get(self.trainer_url + '/completed_jobs.json').content)
            if 'models' in data:
                for model in data["models"]:
                    if model["status"] != "Error":
                        self.db_manager.set_experiment_results(model)
        except Exception as err:
            pass
    def start(self):
        self.job_scheduler.start()

    #exp
    def start_from_script(self):
        try:
            #subprocess.call("run_training_service_occ.sh", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.call(["python", "/home/hy/Documents/occupancy/train_ssh.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as err:
            logger.error("start from script err: %s", err.message)
            raise err

    def stop(self):
        self.job_scheduler.stop()
    def get_experiment_status(self, eid):
        try:
            exp = self.db_manager.get_experiment_global(eid)
        except Exception as e:
            raise Exception("Can't find global experiment ID locally.")
        try:
            #todo:customize
            res = {}
            res["id"] = eid
            res["data_status"] = exp.data_status
            res["train_status"] = exp.train_status
            res["train_job_id"] = exp.train_job_id
            res["accuracy"] = exp.accuracy
            res["epoch"] = exp.epoch
            res["learning_rate"] = exp.learning_rate
            res["loss_train"] = exp.loss_train
            res["loss_val"] = exp.loss_val
            res["elapsed"] = exp.elapsed
            res["progress"] = exp.progress
            res["url"] = config.general.self_desc + ":" + config.general.trainer_port + "/models/" + exp.train_job_id
            return res
        except Exception as e:
            raise e
    def queue_experiment(self, exp_id, data_job_id, data):
        try:
            local_eid = self.db_manager.add_experiment(exp_id, data_job_id, data)
        except Exception as err:
            logger.error("db_manager.add_experiment err: %s", err.message)
            raise err
        try:
            self.job_scheduler.add_session_to_queue(local_eid)
        except Exception as err:
            logger.error("cannot start job scheduler for exp id: %s", exp_id)
            raise err
        return str(exp_id)
    def get_service_status(self):
        proc = subprocess.Popen(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv"], stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode:
            return "Failed"
        return out


