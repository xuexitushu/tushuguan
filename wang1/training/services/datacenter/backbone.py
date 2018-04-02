#backbone.py
import os
import json
import requests
import config
import db
from services.backbone_base import Backbone, create_url_from_ip
from flask import abort
from log import logger

class BackboneDatacenter(Backbone):
    def __init__(self):
        self.db = config.general.local_db
        self.db_manager = db.DataBaseManager(self.db)
        self.source_folder = config.general.source_folder
        for trainer in config.sub_services:
            address = create_url_from_ip(trainer.ip, trainer.port)
            self.db_manager.add_training_node(trainer.name, address)


    def list_folder(self):
        '''
        :return: in .json format, list of
        directories in first level, description files, content of description files
        '''
        # Joining the base and the requested path
        abs_path = self.source_folder
        logger.debug("data center searches folders at %s", abs_path)
        # Return 404 if path doesn't exist
        if not os.path.exists(abs_path):
            raise ValueError("datacenter source folder does not exist!")
        dict = []
        # check if path is a dir and serve
        if os.path.isdir(abs_path):
            dirs = [s for s in os.listdir(abs_path)]
            logger.debug("data folders: %s", dirs)
            for item in dirs:
                res = {}
                item_path = os.path.join(abs_path,item)
                if not os.path.isdir(item_path):
                    continue
                desc_file = os.path.join(item_path, "desc.txt")
                if os.path.exists(desc_file):
                    with open(desc_file, "r") as f:
                        res["description"] = f.read()
                res["id"] = os.path.basename(item_path)
                dict.append(res)
        return dict
    def list_subdirs(self):
        '''
        :return: in .json format, list of
        directories in every level, description files, content of description files
        '''
        # Joining the base and the requested path
        abs_path = self.source_folder
        # Return 404 if path doesn't exist
        if not os.path.exists(abs_path):
            raise ValueError("datacenter source folder does not exist!")
        dict = []
        # check if path is a dir and serve
        if os.path.isdir(abs_path):
            for dir, subdir, filename in os.walk(abs_path):
                res = {}
                if os.path.isdir(dir):
                    res["folder id"] = dir
                    fdirs = [s for s in os.listdir(dir) if '.txt' in s and 'desc' in s]
                    if len(fdirs) > 0:
                        fn = os.path.join(dir,fdirs[0])
                        res["desc_name"] = fn
                        '''
                        with open(fn, 'r') as file:
                            lines = file.read()
                        res["desc_content"] = lines
                        '''
                    dict.append(res)
                    res = json.dumps(dict)
        return res

    def list_folder_files(self):
        # Joining the base and the requested path
        abs_path = self.source_folder
        # Return 404 if path doesn't exist
        if not os.path.exists(abs_path):
            raise ValueError("datacenter source folder does not exist!")
        dict = []
        # check if path is a dir and serve
        if os.path.isdir(abs_path):
            for dir, subdir, filename in os.walk(abs_path):
                res = {}
                res["folder"] = dir
                res["subdir"] = subdir
                filename = str(filename)
                if '.txt' in filename:
                    res["desc"] = filename
                elif ('.png' in filename) or ('.jpg' in filename):
                    res["datafiles"] = filename
                dict.append(res)
        return dict
