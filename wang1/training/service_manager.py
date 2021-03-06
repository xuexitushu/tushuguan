#service_manager.py
import flask
import config
import threading
import services
from log import logger
app = flask.Flask(__name__)
logger.info("Service update interval: %s "
            % config.general.service_update_interval)
# Python way of abstract factory pattern? :)
if config.general.type == services.CONTROLLER:
    from services.controller import interface
elif config.general.type == services.TRAINER:
    from services.trainer import interface
elif config.general.type == services.TRAINER_OCC:
    from services.trainer_occ import interface
elif config.general.type == services.DATACENTER:
    from services.datacenter import interface
else:
    msg = "Sorry no implementation available for this service!"
    logger.error(msg)
    raise NotImplementedError(msg)

def update_thread(f_stop):
    """ Keeps DB up to date """
    interface.backbone.sync_db()
    if not f_stop.is_set():
        threading.Timer(config.general.service_update_interval,
                        update_thread,
                        [f_stop]).start()
f_stop = threading.Event()
update_thread(f_stop)

def start():
    logger.info("%s started", config.general.name)
    interface.backbone.start()

def stop():
    logger.info("%s stopped", config.general.name)
    f_stop.set()
    interface.backbone.stop()

try:
    app.register_blueprint(interface.blueprint, url_prefix=config.general.prefix)
except Exception as err:
    logger.warning("Can't add %s interface: %s", config.general.name, err)
