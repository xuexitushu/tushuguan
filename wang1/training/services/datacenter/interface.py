#interface.py
import os
import config
from log import logger
from flask import jsonify, Blueprint, make_response
from services.datacenter import backbone

blueprint = Blueprint(__name__, __name__)
backbone = backbone.BackboneDatacenter()

@blueprint.route('/', methods=['GET'])
def idle():
    return success()

@blueprint.route('/index.json', methods=['GET'])
def list_folder():
    try:
        return success(backbone.list_folder())
    except Exception as err:
        return failed(err.message)

@blueprint.route('/list_folder_files', methods=['GET'])
def list_folder_files():
    try:
        return jsonify({"success": backbone.list_folder_files()})
    except Exception as err:
        return jsonify({"error":err.message})

def failed(error = "Unknown"):
    return make_response(jsonify({'error': str(error)}), 404)

def success(msg = "OK"):
    return make_response(jsonify({'success' : msg}), 200)

def success_or_fail(func):
    try:
        return success(func())
    except Exception as err:
        return failed(err.message)

