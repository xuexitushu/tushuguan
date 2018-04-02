#client/  train.py
import requests
import cv2
import json
import base64
import ntpath
import argparse
import random
import time

def request_training(node_id, job_id, params):
    json_data = json.dumps(params)
    return requests.get(host + "/" + str(node_id) + "/" + job_id, data = json_data).content

def main():
    global host
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--node", default=1)
    parser.add_argument("--net", default="lenet")
    parser.add_argument("--frm", default="caffe")
    parser.add_argument("--data", required=True)
    parser.add_argument("--lr", default=random.uniform(0.001, 0.01))
    parser.add_argument("--name", default="experiment_"+str(time.time()))
    parser.add_argument("--project", default="test_project")
    parser.add_argument("--user", default="mobilityai")
    args = parser.parse_args()
    host = "http://" + args.ip + ":8000/train"
    params = {}
    params['method'] = "standard"
    params['framework'] = args.frm
    params['model_name'] = args.name
    params['train_epochs'] = random.randint(10,30)
    params['learning_rate'] = args.lr
    params['standard_networks'] = args.net
    params['dataset'] = args.data
    params['project'] = args.project
    params['user'] = args.user
    print request_training(args.node, args.data, params)

if __name__ == "__main__":
    main()



