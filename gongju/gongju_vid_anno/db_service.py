#db_service.py
# provides database services for inserting and loading

import json
import datetime
from sqlalchemy import and_
from datetime import datetime
from database import db_session
from models import FrameAnnotation, LabelClass, LabelState, Project, RawData


# functions
class DBService:

    def setup(self, project_id, raw_data_name):
        raw_data_entry = db_session.query(RawData).filter(RawData.name == raw_data_name, RawData.project_id == project_id).first()
        if  raw_data_entry is None:
            new_raw_data = RawData(raw_data_name, project_id)
            db_session.add(new_raw_data)
            db_session.commit()
            db_session.refresh(new_raw_data)
            _raw_data_id = new_raw_data.id
        else:
            _raw_data_id = raw_data_entry.id
        self.data_id = _raw_data_id
        return _raw_data_id


    @staticmethod
    def export_nrplatecsv():
        result = []
        query = db_session.query(FrameAnnotation, RawData)
        join = query.join(RawData, and_(FrameAnnotation.raw_data_id == RawData.id))
        filtered = join.filter(FrameAnnotation.label_data != '[]')
        res = filtered.all()
        for r in res:
            folder = r.RawData.name
            frame = r.FrameAnnotation.frame_name
            data = r.FrameAnnotation.label_data
            data_json = json.loads(data)
            nrplate = data_json[0]['comment']
            nrplate = nrplate.replace(",",";")
            rows = data_json[0]['class']
            state = data_json[0]['state']
            csv_row = folder+","+frame+","+rows+","+nrplate+","+state
            result.append(csv_row)
        return result

    @staticmethod
    def get_annotated_frames(raw_data_id):
        result = []
        query = db_session.query(FrameAnnotation, RawData)
        join = query.join(RawData, and_(FrameAnnotation.raw_data_id == RawData.id))
        filtered = join.filter(
            FrameAnnotation.label_data != '[]',
            RawData.id == raw_data_id
        )
        res = filtered.all()
        for r in res:
            frame = r.FrameAnnotation.frame
            result.append(frame)
        return result

    @staticmethod
    def load_video_annotations(raw_data_id):
        result = {}
        query = db_session.query(FrameAnnotation, RawData)
        join = query.join(RawData, and_(FrameAnnotation.raw_data_id == RawData.id))
        res = join.all()
        for r in res:
            frame = r.FrameAnnotation.frame
            labels = r.FrameAnnotation.label_data
            #ann = {}
            #ann['frame'] = frame
            #ann['labels'] = labels
            result[frame] = labels
            #result.append(ann)
        return result

    @staticmethod
    def get_project_map():
        projects = db_session.query(Project).all()
        project_map = {}
        for project in projects:
            project_map[project.name] = project.id
        return project_map

    @staticmethod
    def get_label_classes(project_id):
        klasses = db_session.query(LabelClass).filter(LabelClass.project_id == project_id)
        klass_map = {}
        for klass in klasses:
            klass_map[klass.id] = klass.name
        return klass_map

    @staticmethod
    def get_label_states(class_id):
        states = db_session.query(LabelState).filter(LabelState.label_class_id == class_id)
        state_map = {}
        for state in states:
            state_map[state.id] = state.name
        return state_map



    def update_video_annotations(self, data):
        # currently we do this the brute force way:
        # delete all then bulk insert
 
        self.data_id = 1
        q = db_session.query(FrameAnnotation)
        # remove
        '''q = db_session.query(FrameAnnotation)
        for r in remove:
            record = q.filter(FrameAnnotation.frame == r).first()
            if record is not None:
                db_session.delete(record)'''
        # update
        #objects = []
        for i,v in enumerate(data,start=1):
            if v is not None:
                fe = self.createFrameEntry(i,i,v)
                db_session.merge(fe)
        #db_session.bulk_save_objects(objects)
        db_session.commit()
        print "bulk done"

    def createFrameEntry(self, frame, frame_name, annotation_data):
        if self.data_id is None:
            return -1
        data_list = []
        for data_entry in annotation_data:
            data = {}
            data['class'] = data_entry['label']['class']
            data['state'] = data_entry['label']['state']
            data['comment'] = data_entry['label']['comment']
            transform_str = {}
            transform_str['x'] = data_entry['x']
            transform_str['y'] = data_entry['y']
            transform_str['h'] = data_entry['h']
            transform_str['w'] = data_entry['w']
            data['transform'] = transform_str
            data_list.append(data)
        data_list = str(json.dumps(data_list))
        result = FrameAnnotation(self.data_id, frame, frame_name, data_list, datetime.now())
        return result

    def insert_or_update(self, frame, frame_name, annotation_data):
        if self.data_id is None:
            return -1
        data_list = []
        for data_entry in annotation_data:
            data = {}
            data['class'] = data_entry['label']['class']
            data['state'] = data_entry['label']['state']
            data['comment'] = data_entry['label']['comment']
            transform_str = {}
            transform_str['x'] = data_entry['x']
            transform_str['y'] = data_entry['y']
            transform_str['h'] = data_entry['h']
            transform_str['w'] = data_entry['w']
            data['transform'] = transform_str
            data_list.append(data)

        data_list = str(json.dumps(data_list))
        result_id = None
        q = db_session.query(FrameAnnotation)
        q = q.filter(FrameAnnotation.frame == frame, FrameAnnotation.raw_data_id == self.data_id)
        record = q.first()
        if record is not None:
            result_id = record.id
            record.label_data = data_list
            record.last_updated = datetime.now()
            db_session.commit()
        else:
            f = FrameAnnotation(self.data_id, frame, frame_name, data_list, datetime.now())
            db_session.add(f)
            db_session.commit()
            db_session.refresh(f)
            result_id = f.id
        return result_id

    
    def load_entry(self, frame):
        if self.data_id is not None:
            q = db_session.query(FrameAnnotation)
            q = q.filter(FrameAnnotation.frame == frame, FrameAnnotation.raw_data_id == self.data_id)
            record = q.first()
            if record is not None:
                return record.label_data
        return None


