#__init__.py
import os
import json
from os.path import expanduser
home = expanduser("~")

from shutil import copyfile

options = {}
general = None
controller = None
data_center = None
sub_services = []

LOCAL_RESOURCE_FOLDER = os.path.dirname(os.path.abspath(__file__))
PROGRAM_NAME = "spajm"


class Config:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def init(topology_file_path, config_file_name, replace_old=False, use_relative=False):
    global options, general, controller, sub_services, data_center

    if not os.path.exists(topology_file_path):
        raise IOError("Topology file does not exist")

    with open(topology_file_path, "r") as f:
        options = json.load(f)

    if use_relative:
        if not os.path.exists(config_file_name):
            raise IOError("Config file does not exist")

        with open(config_file_name, "r") as f:
            general_options = json.load(f)
    else:
        application_home = os.path.join(home, "." + PROGRAM_NAME)
        if not os.path.exists(application_home):
            os.makedirs(application_home)

        general_config_file_path = os.path.join(application_home,
                                                config_file_name)
        general_config_local = os.path.join(LOCAL_RESOURCE_FOLDER,
                                            config_file_name)

        local_time = os.path.getmtime(general_config_local)

        if not os.path.exists(general_config_file_path):
            copyfile(general_config_local, general_config_file_path)

        target_time = os.path.getmtime(general_config_file_path)

        if replace_old and local_time > target_time:
            print "Global config file has been replaced with the local one"
            copyfile(general_config_local, general_config_file_path)

        with open(general_config_file_path, "r") as f:
            general_options = json.load(f)

    general = Config(**general_options["app"])
    controller = Config(**options["controller"])
    data_center = Config(**options["datacenter"])

    if data_center.ip == general.ip:
        data_center.ip = "127.0.0.1"

    for s in options["subservices"]:
        if s["ip"] == general.ip:
            s["ip"] = "127.0.0.1"
        sub_services.append(Config(**s))


