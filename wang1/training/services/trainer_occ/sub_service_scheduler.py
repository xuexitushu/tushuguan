#sub_service_scheduler.py
import os
import threading
import Queue
import time
import config
from log import logger

class Session(object):
    def __init__(self):
        process = None

# TODO: Replace hard coded status codes with something smarter.
class SubServiceScheduler(object):
    # stores active session processes
    sessions = {}
    # stores sessions in queue
    session_queue = Queue.Queue(maxsize=100)
    # stored experiment id of the active session
    active_session = None
    def __init__(self, task_runner):
        self.f_stop = threading.Event()
        self.task_runner = task_runner
        self.db_manager = self.task_runner.db_manager
        self.update_interval = 5
    def start(self):
        """ Initialized a thread to continuously monitor the process queue.
            When the active job is completed, new session in the queue is started. """
        def f():
            if self.session_queue.qsize() > 0:
                if not self.active_session:
                    self.active_session = self.session_queue.get()
                    eid = self.active_session
                    self.sessions[eid] = Session()
                    try:
                        self.db_manager.set_experiment_data_status(eid, "In Progress")
                        p_job = self.task_runner.run(eid)
                        self.sessions[eid].job_process = p_job
                    except Exception as err:
                        self.stop_task(eid)
                        self.db_manager.set_experiment_data_status(eid, "Failed")
                        self.db_manager.set_experiment_train_status(eid, "Failed")
                        print "Experiment failed due to: " + err.message
            # Continously update the DB with the actual training session outcomes
            self.update_all_experiment_status()
            # Continue until stop has been signaled
            if not self.f_stop.is_set():
                threading.Timer(self.update_interval, f).start()
        self.f_stop = threading.Event()
        if self.task_runner:
            f()
    def stop(self):
        self.f_stop.set()
    def add_session_to_queue(self, eid):
        self.session_queue.put(eid)
        self.db_manager.set_experiment_data_status(eid, "Waiting")
    def update_all_experiment_status(self):
        """ Gets experiments with 'In Progress' status. Marks them as 'Done' if they are finished already. """
        try:
            exps = self.db_manager.get_experiments_in_progress()
        except Exception as err:
            return False
        print exps
        for exp in exps:
            try:
                if self.task_runner.update_status(exp) == "Finished": # means the process is finished successfully
                    self.stop_task(exp.id)
                    self.db_manager.set_experiment_data_status(exp.id, "Done")
                elif self.task_runner.update_status(exp) == "Failed": # means the process failed
                    self.stop_task(exp.id)
                    self.db_manager.set_experiment_data_status(exp.id, "Failed")
                    self.db_manager.set_experiment_train_status(exp.id, "Failed")
            except Exception as err:
                self.stop_task(exp.id)
                self.db_manager.set_experiment_data_status(exp.id, "Failed")
                self.db_manager.set_experiment_train_status(exp.id, "Failed")
                print "Can't update status of experiment: " + str(exp.id) + "\nFailed due to: " + err.message
        return True
    def stop_task(self, eid):
        """ Force an 'in progress' training session to stop. """
        if not self.db_manager.is_exp_in_progress(eid):
            return
        self.active_session = None
        sess = self.sessions[eid]
        if hasattr(sess, 'process'):
            try:
                sess.process.terminate()
            except AttributeError:
                pass
        self.db_manager.set_experiment_data_status(eid, "Stopped")
        self.sessions.pop(eid, None)
    def is_idle(self):
        return self.active_session is None


