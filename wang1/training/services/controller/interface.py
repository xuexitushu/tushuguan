#controller de interface.py
import os
import config
from log import logger

from flask import jsonify, Blueprint, make_response, request

from services.controller import backbone

blueprint = Blueprint(__name__, __name__)

backbone = backbone.BackboneController()


@blueprint.route('/', methods=['GET'])
def test():
    return success()


@blueprint.route('/ping', methods=['GET'])
def ping_training_nodes():
    return success_or_fail(backbone.ping)


@blueprint.route('/list_data', methods=['GET'])
def list_data():
    return success_or_fail(backbone.list_available_data)


@blueprint.route('/list_nodes', methods=['GET'])
def list_nodes():
    return success_or_fail(backbone.list_nodes)


@blueprint.route('/gpu_usage', methods=['GET'])
def get_gpu_usage():
    return success_or_fail(backbone.get_gpu_usage)


@blueprint.route('/list_networks', methods=['GET'])
def list_networks():
    return jsonify({"status":"NotImplemented"})


@blueprint.route('/list_projects', methods=['GET'])
def list_projects():
    res = backbone.list_projects()
    return jsonify({"projects":res})


@blueprint.route('/list_exp/<int:proj_id>', methods=['GET'])
def list_exp(proj_id):
    name, res = backbone.get_experiments_by_project_id(proj_id)
    return jsonify({name : res})


@blueprint.route('/list_exp/all', methods=['GET'])
def list_all_exp():
    res = backbone.get_all_experiments()
    return jsonify({"experiments" : res})


@blueprint.route('/exp/<int:exp_id>', methods=['GET'])
def get_experiment_status(exp_id):
    try:
        res = backbone.get_experiment_status(exp_id)
        return jsonify(res)
    except Exception as err:
        return failed(err.message)

"""
@blueprint.route('/exp/<int:exp_id>/mdb', methods=['POST'])
def upload_to_modeldb(exp_id):
    res = backbone.send_exp_to_modeldb(exp_id)
    return jsonify({"result": res})
"""

@blueprint.route('/train/<int:node_id>/<string:data_job_id>', methods=['GET'])
def start_training(node_id, data_job_id):
    try:
        res = backbone.queue_experiment(node_id, data_job_id, request.data)
        logger.info("backbone.queue_experiment retuns: %s", res)
        return res
    except Exception as e:
        return failed(e.message)


def failed(error = "Unknown"):
    return make_response(jsonify({'error': str(error)}), 404)


def success(msg = "OK"):
    return make_response(jsonify({'success' : msg}), 200)


def success_or_fail(func):
    try:
        return success(func())
    except Exception as err:
        return failed(err.message)



