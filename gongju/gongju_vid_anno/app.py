#app.py
# main script of annotation app that defines the routes

# imports
import datetime
import json
import config
import sys
import os

# from video_controller import VideoController
from db_service import DBService
from flask import Flask, Response, render_template, request
from database import db_session


# init
app = Flask(__name__)
_raw_data_id = None
_raw_data_name = ""
db_service = DBService()

# routes
@app.route("/")
def index():
    project_map = db_service.get_project_map()
    selected_id = config.project_id
    return render_template("index.html", project_map=project_map, selected_project=selected_id)

@app.route("/init", methods=['POST'])
def init():
    project_id = request.json['project_id']
    raw_data_name = request.json['raw_data_name']
    raw_data_id = db_service.setup(project_id, raw_data_name)
    return str(raw_data_id)

@app.route("/get_classes", methods=['POST'])
def get_class():
    project_id = request.json['project_id']
    label_classes = db_service.get_label_classes(project_id)
    return json.dumps(label_classes)

@app.route("/get_states", methods=['POST'])
def get_state():
    class_id = request.json['class_id']
    label_states = db_service.get_label_states(class_id)
    return json.dumps(label_states)

@app.route("/get_annotated_frames", methods=['POST'])
def get_annotated_frames():
    rd_id = request.json['raw_data_id']
    result = db_service.get_annotated_frames(rd_id)
    return json.dumps(result)

@app.route("/update", methods=['POST'])
def update():
    # Write Data into DB
    andata = request.json['annotation_data']
    frame = request.json['frame']
    frame_name = request.json['frame_name']
    db_service.insert_or_update(frame, frame_name, andata)

    # Load Data for next Frame
    next_frame = request.json['next_frame']
    next_frame_annotation = db_service.load_entry(next_frame)
    return json.dumps(next_frame_annotation)

@app.route("/get_annotation", methods=['POST'])
def get_annotation():
    # Load Data for next Frame
    next_frame = request.json['next_frame']
    next_frame_annotation = db_service.load_entry(next_frame)
    return json.dumps(next_frame_annotation)

#/home/hy/Documents/silanno_andreas/cache
@app.route("/save_video_annotations", methods=['POST'])
def save_video_annotations():
    print request.json['name']
    with open("/home/hy/Documents/silanno_andreas/cache"+os.sep+request.json['name']+'.json','w+') as cachefile:
        json.dump(request.json,cachefile)
    return "saved file"

@app.route("/load_video_annotations", methods=['POST'])
def load_video_annotations():
    result = None
    _raw_data_name = request.json['name']
    print request.json['name']
    with open("cache"+os.sep+_raw_data_name+'.json') as cachefile:
        result= json.dumps(cachefile.read())
    return result

@app.route("/update_video_annotations",methods=['POST'])
def update_video_annotations():
    #print sys.getsizeof(request.json)
    #db sync implemented, not well tested, temporarily deactivated
    #db_service.update_video_annotations(request.json)
    with open("cache"+os.sep+_raw_data_name+'_cache.json','w+') as cf:
        json.dump(request.json,cf)
    return str(1)


@app.route("/load_video_annotations_db",methods=['POST'])
def load_video_annotations_db():
    rd_id = request.json['raw_data_id']
    result = db_service.load_video_annotations(rd_id)
    return json.dumps(result)


# db teardown
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# start main loop
if __name__ == "__main__":
    app.run(debug=True)
    #app.run()


