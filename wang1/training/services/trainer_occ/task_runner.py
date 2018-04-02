#task_runner.py
import json
import time
import subprocess
import os
import requests
import config
from log import logger

# TODO: Generalize this, remove DIGITS related stuff and subtype them.
class TaskRunner(object):
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.proc = -1
        self.is_cached = False
    def run(self, eid):
        self.is_cached = False
        exp = self.db_manager.get_experiment(eid)
        data_folder = os.path.join(config.general.cache, exp.data_job_id)
        #data_folder = os.path.join(config.general.cache, exp.data_job_id)
        if os.path.exists(data_folder):
            if os.path.exists(os.path.join(data_folder, "mobility")):
                self.is_cached = True
                return 0
        copy_from = os.path.join(config.general.data_location, exp.data_job_id)
        copy_to = config.general.cache
        copy_method = config.general.copy_method
        try:
            if copy_method == "local":
                self.proc = self.copy_from_local(copy_from, copy_to)
            else:
                self.proc = self.copy_from_remote(copy_from, copy_to)
        except Exception as e:
            raise e
        return 0
    def copy_from_local(self, copy_from, copy_to):#
        try:
            proc = subprocess.Popen(["cp", "-r", copy_from, copy_to], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as err:
            raise err
        return proc
    def copy_from_remote(self, copy_from, copy_to):
        try:
            proc = subprocess.Popen(["sshpass", "-p", "1du%Kaye", "scp", "-r", copy_from, copy_to],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as err:
            raise err
        return proc
    def start_training(self, exp):
        # continue the chain here, deliver the training to digits (with parameters)
        uid = self.db_manager.create_uid_for_params(exp.exp_id, exp.data_job_id)
        # read params
        with open(uid, "r") as f:
            params = json.load(f)
            data = json.loads(str(params))
        time.sleep(5)
        try:
            #todo:customize
            subprocess.call(["run_training_service_occ.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #proc = subprocess.Popen(["sh", "restart_training.sh", "dataid", "uid"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #subprocess.Popen("sh", "start_training.sh", "dataid", "uid", erro)
            '''
            cookies = {
                "username" : "mobilityai"
            }
            files = {
                'method': (None, data["method"]),
                'standard_networks': (None, data["standard_networks"]),
                'train_epochs': (None, str(data["train_epochs"])),
                'framework': (None, data["framework"]),
                'model_name': (None, data["model_name"]),
                'dataset': (None, data["dataset"]),
            }
            ip = "http://" + config.general.trainer_ip + ":" + config.general.trainer_port
            ############################
            response = json.loads(str(requests.post(ip + '/models/images/classification.json', cookies=cookies,
                                     files=files).content))

            logger.info("response %s", response)
            if 'errors' in response:
                raise Exception(str(response['errors']))
            train_id = response["job id"]
            self.db_manager.set_experiment_train_job_id(exp.id, train_id)
            '''
        except Exception as err:
            raise err
        return "Finished"
    def update_status(self, exp):
        if self.is_cached:
            return self.start_training(exp)
        out, err = self.proc.communicate()
        print out, err
        if self.proc.returncode:
            return "Failed"
        else:
            data_folder = os.path.join(config.general.cache, exp.data_job_id)
            approval_file = os.path.join(data_folder, 'mobility')
            f = open(approval_file, "w+")
            return self.start_training(exp)


