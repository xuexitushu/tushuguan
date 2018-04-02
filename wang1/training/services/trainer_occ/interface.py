#trainer_occ interface.py
#customized
import os
import config
from log import logger
from flask import jsonify, Blueprint, make_response, request
from services.trainer_occ import backbone
blueprint = Blueprint(__name__, __name__)
# TODO: This interface should support multiple trainer backbone (not only Digits trainer!!!)
# Use the same interface for multiple trainer implementations
backbone = backbone.BackboneTrainer()
#ok
@blueprint.route('/', methods=['GET'])
def idle():
    return success()
#idle
@blueprint.route('/status', methods=['GET'])
def get_status():
    #logger.debug("get_status called, service status %s", backbone.service_status)
    return jsonify({"status":backbone.service_status})
#internal error
@blueprint.route('/gpu', methods=['GET'])
def get_gpu_status():
    res = backbone.get_service_status()
    return jsonify({"status":res})
#3
@blueprint.route('/queue/<int:exp_id>/<string:data_job_id>', methods=['GET'])
def queue_experiment(exp_id, data_job_id):
    try:
        eid = backbone.queue_experiment(exp_id, data_job_id, request.data)
        return jsonify({"result": eid})
    except Exception as err:
        logger.error("Error by queueing experiment %s: %s", exp_id, err.message)
        return failed(err.message)
#ok
@blueprint.route('/usage', methods=['GET'])
def get_usage():
    return jsonify({"status": "NotImplemented"})
#start from script
@blueprint.route('/start_script', methods=['GET'])
def get_start_resp():
    try:
        backbone.start_from_script()
        return jsonify({"status": "ok start from script"})
    except Exception as err:
        logger.error("Error by starting from script %s", err.message)
        return failed(err.message)
#3
@blueprint.route('/exp/<int:exp_id>', methods=['GET'])
def get_experiment_status(exp_id):
    try:
        res = backbone.get_experiment_status(exp_id)
        return jsonify({"status" : res})
    except Exception as e:
        return failed(e.message)

def failed(error="Failed"):
    return make_response(jsonify({'error': error}), 404)

def success(msg = "OK"):
    return make_response(jsonify({'result' : msg}), 200)


