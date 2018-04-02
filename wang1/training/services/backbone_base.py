#backbone_base.py
import requests
#from log import logger

def create_url_from_ip(ip, port):
    return "http://" + str(ip) + ":" + str(port)

class Backbone(object):
    def __init__(self):
        pass
    def sync_db(self):
        pass
    def start(self):
        pass
    def stop(self):
        pass
    def is_sub_service_alive(self, service_address):
        try:
            # logger.debug("checking %s if it is alive!", service_address)
            requests.get(service_address)
            return True;
        except Exception:
            return False;

