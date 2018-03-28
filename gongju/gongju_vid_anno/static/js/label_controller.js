//label class
function Label(label_class, state, comment) {
    this.class = label_class;
    this.state = state;
    this.comment = comment;
}

//annotation fabric class
fabric.AnRect = fabric.util.createClass(fabric.Rect, {
    type: 'anRect',

    initialize: function (options) {
        options || (options = {});
        this.callSuper('initialize', options);
        this.set('label', options.label || null);
        this.set('transparentCorners', false);
        this.set('hasRotatingPoint', false);

    },

    toObject: function () {
        return fabric.util.object.extend(this.callSuper('toObject'), {
            label: $.extend({}, this.get('label'))
        })
    },

    _render: function (ctx) {
        this.callSuper('_render', ctx);
        ctx.font = 'bold 12px Helvetica';
        ctx.fillStyle = '#B0E57C';
        var classMap = _labelController.getClasses();
        var name = classMap[this.label.class].name;
        var state = classMap[this.label.class].states[this.label.state];
        ctx.fillText(name,
            -this.width / 2, -this.height / 2 + 12);
        ctx.fillStyle = '#FFAEAE';
        ctx.fillText(state,
            -this.width / 2, -this.height / 2 + 25);
    }
});

fabric.AnRect.fromObject = function (obj, callback) {
    var newAnRect = new fabric.AnRect(obj);
    return newAnRect;
}

//class for dealing and manipulating labels
function LabelController(canvasElement) {
    var _canvas = new fabric.Canvas(canvasElement);
    var _currentRect = null;
    var _copy = false;
    var _dataList = $('#ticks');
    var _frameAnnotations = [];
    var _keyFrames = [];
    var _keyFrameAnnotationCache = {};
    var _dirty = false;
    var _copyMode = false;
    var _currentFrame = 0;
    var _overWriteEmpty = true;
    var _writeMode = false;
    var _propagate = false;
    var _fillDelta = true;
    var _classes = null;
    var _playing = false;
    var _self = this;
    var _debug = true;
    var _sfb = $('#sb-btn');
    var _sbb = $('#sf-btn');
    var _syncRoutine = null;
    var _autosave = true;
    this.debugOut = function (msg) {
        if (_debug) {
            console.log(msg);
        }
    }

    this.printKeyFrames = function () {
        console.log(_keyFrames);
    }

    this.getCachedFrames = function () {
        return _frameAnnotations;
    }

    this.getClasses = function () {
        return _classes;
    }

    this.updateButtons = function () {
        if (_writeMode) {
            if (_propagate) {
                _sfb.attr('class', 'btn btn-danger');
                _sbb.attr('class', 'btn btn-danger');
                return;
            }
            _sfb.attr('class', 'btn btn-warning');
            _sbb.attr('class', 'btn btn-warning');
            return;
        }
        _sfb.attr('class', 'btn btn-info');
        _sbb.attr('class', 'btn btn-info');
        return;
    }

    this.containsLabel = function (lbl, objs) {
        for (var obj of objs) {
            if (obj.left == lbl.left
                && obj.top == lbl.top
                && obj.height == lbl.height
                && obj.width == lbl.width
                && obj.label.class == lbl.label.class
                && obj.label.state == lbl.label.state
                && obj.label.comment == lbl.label.comment
            ) {
                return true;
            }
        }
        return false;
    }


    this.framesEqual = function (frameA, frameB) {
        var annoA = _frameAnnotations[frameA];
        var annoB = _frameAnnotations[frameB];
        return this.annotationsEqual(annoA, annoB);
    }

    this.annotationsEqual = function (annoA, annoB) {
        //check if both empty or null
        if (this.annotationEmpty(annoA) && this.annotationEmpty(annoB)) {
            return true;
        }

        //check for null
        if (annoA == null ^ annoB == null) {
            return false;
        }

        //check lenght
        if (annoA.objects.length != annoB.objects.length) {
            return false;
        }
        //deep check members

        var eq = true;
        for (var lba of annoA.objects) {
            eq = eq && this.containsLabel(lba, annoB.objects);
        }

        return eq;
    }

    this.toggleWrite = function (value = null) {
        if (value == null) {
            _writeMode = !_writeMode;
        } else {
            _writeMode = value;
        }
        if (!_writeMode) {
            _propagate = false;
        }
        this.updateButtons();
        this.debugOut("Write Mode: " + _writeMode);
    }

    this.togglePropagation = function () {
        if (_writeMode) {
            _propagate = !_propagate;
            this.updateButtons();
            this.debugOut("Prop. Mode: " + _propagate);
        }
    }

    this.initVideo = function (w, h, v) {
        _canvas.setWidth(w);
        _canvas.setHeight(h);
    }

    this.setBackground = function (imgElement) {
        var imgInstance = new fabric.Image(imgElement)
        _canvas.setWidth(imgElement.naturalWidth);
        _canvas.setHeight(imgElement.naturalHeight);
        _canvas.setBackgroundImage(imgInstance)
        _canvas.calcOffset();
        _canvas.renderAll();
    }

    this.getObjects = function () {
        var result = [];
        var objects = _canvas.getObjects();
        for (var i = 0, o; o = objects[i]; i++) {
            var entry = {};
            entry['label'] = o.label;
            entry['x'] = o['left'];
            entry['y'] = o['top'];
            entry['h'] = Math.floor(o.getHeight());
            entry['w'] = Math.floor(o.getWidth());
            result.push(entry);
        }
        return result;
    }

    this.objectsToMeta = function (aRect) {
        if (aRect == null) {
            return [];
        }
        var result = []
        for (var o of aRect.objects) {
            var entry = {};
            entry['label'] = o.label;
            entry['x'] = o['left'];
            entry['y'] = o['top'];
            entry['h'] = o['height'];
            entry['w'] = o['width'];
            result.push(entry);
        }
        return result;
    }

    this.metaToRect = function (meta) {
        var width = meta.transform.w;
        var height = meta.transform.h;
        var x = meta.transform.x;
        var y = meta.transform.y;
        var label = new Label(meta.class, meta.state, meta.comment);
        var rect = new fabric.AnRect({
            fill: 'rgba(0,256,256,0.1)',
            left: x,
            top: y,
            width: width,
            height: height,
            strokeWidth: 1,
            cornerColor: 'rgba(0, 200, 200, 1)',
            stroke: 'rgba(0,256,256,1)',
            transparentCorners: false,
            hasRotatingPoint: false,
            label: label
        });
        return rect.toObject();
    }

    this.metaToObj = function (x, y, w, h, cls, state, cmt) {
        var label = new Label(cls, state, cmt);
        var rect = new fabric.AnRect({
            fill: 'rgba(0,256,256,0.1)',
            left: x,
            top: y,
            width: w,
            height: h,
            strokeWidth: 1,
            cornerColor: 'rgba(0, 200, 200, 1)',
            stroke: 'rgba(0,256,256,1)',
            transparentCorners: false,
            hasRotatingPoint: false,
            label: label
        });
        return rect.toObject();
    }


    this.initInput = function (classObject) {
        _classes = classObject;
        $('#class_input').html("");
        for (var key in _classes) {
            $('#class_input')
                .append($('<option>', { value: key })
                    .text(_classes[key].name));
        }
        $('#class_input').trigger('change');
    }


    this.updateControls = function () {
        if (_currentRect != null) {
            var left = Math.floor(_currentRect.getLeft());
            var top = Math.floor(_currentRect.getTop());
            var width = Math.floor(_currentRect.getWidth());
            var height = Math.floor(_currentRect.getHeight());
            $('#transform').html(left + "," + top + "," + width + "," + height);
            $('#class_input').val(_currentRect.label.class);
            $('#state_input').val(_currentRect.label.state);
            $('#comment_input').val(_currentRect.label.comment);
            //console.log($('#state_input').val())
        }
    }

    this.clearControls = function () {
        $('#transform').html("");
        //$('#class_input').val(0);
        //$('#class_input').prop('disabled',true)
        //$('#state_input').val(-1);
        //$('#state_input').prop('disabled',true)
        $('#class_input')[0].selectedIndex = 0;
        $('#state_input')[0].selectedIndex = 0;
        //$('#class_input').val(1);
        //$('#state_input').val("CH");
        $('#comment_input').val("");
        $('#comment_input').attr('placeholder', "No Label Selected");
        $('#comment_input').prop('disabled', true);
    }

    this.updateLabelComment = function (comment) {
        if (_currentRect != null) {
            _currentRect.label.comment = comment;
        }
    }

    this.updateStates = function (klass, trigger = true) {
        var states = _classes[klass].states;
        $('#state_input').html("");
        for (var key in states) {
            $('#state_input')
                .append($('<option>', { value: key })
                    .text(states[key]));
        }
        if (trigger) {
            $('#state_input').trigger('change');
        }
    }

    this.updateLabelClass = function (klass) {
        if (_currentRect != null) {
            _currentRect.label.class = klass;
        }
        this.updateStates(klass);
        _canvas.renderAll();
    }

    this.updateLabelState = function (state) {
        if (_currentRect != null) {
            _currentRect.label.state = state;
        }
        _canvas.renderAll();
    }

    this.onObjectSelected = function (e) {
        _currentRect = e.target;
        _dirty = true;
        if (_currentRect.label.class != $('#class_input').val()) {
            _self.updateStates(_currentRect.label.class, false);
        }
        //$('#class_input').prop('disabled',false)
        //$('#state_input').prop('disabled',false)
        $('#comment_input').prop('disabled', false);
        $('#comment_input').attr('placeholder', '');
        _self.updateControls();
        $('#class_input').focus();
    }


    this.addAnnoation = function (label = null, x = 540, y = 380, width = 100, height = 100) {
        if (label == null) {
            label = new Label("", "", "");
        }

        var rect = new fabric.AnRect({
            fill: 'rgba(0,256,256,0.1)',
            width: width,
            height: height,
            strokeWidth: 1,
            cornerColor: 'rgba(0, 200, 200, 1)',
            transparentCorners: false,
            hasRotatingPoint: false,
            stroke: 'rgba(0,256,256,1)',
            label: label
        });

        _canvas.add(rect);
        rect.center();
        rect.setCoords();
        _canvas.setActiveObject(rect);
    }

    this.addAnnoationWithClass = function (klass) {
        var label = new Label(klass, "", "");
        this.addAnnoation(label);
    }

    this.addAnnoationWithClassAndState = function (klass, state) {
        var label = new Label(klass, state, "");
        this.addAnnoation(label);
    }


    this.deleteCurrentAnnotation = function () {
        if (_currentRect != null) {
            _canvas.remove(_currentRect);
        }
        this.clearControls();
    }

    this.clearCanvas = function () {
        _canvas.discardActiveGroup();
        _canvas.discardActiveObject();
        _canvas.clearContext(_canvas.contextTop);
        _canvas._objects.length = 0;
        _canvas.clearContext(_canvas.contextContainer);
        _canvas.fire('canvas:cleared');
        _canvas.renderAll();
        this.clearControls();
    }

    this.initSliderTicks = function (ticks) {

        _dataList.empty();
        for (var tick of ticks) {
            _dataList.append("<option>" + tick + "</option>");
        }
    }

    this.addTick = function (frame) {
        _dataList.children().each(function () {
            if ($(this).val() == frame) {
                return;
            }
        });
        _dataList.append("<option>" + frame + "</option>");
    }

    this.removeTick = function (frame) {
        _dataList.children().each(function () {
            if ($(this).val() == frame) {
                $(this).remove();
            }
        });
    }


    this.exportMetaData = function () {
        result = []
        for (var i = 1; i < _frameAnnotations.length; i++) {
            result[i] = this.objectsToMeta(_frameAnnotations[i]);
        }
        return result;
    }

    this.initVideoAnnotation = function (data) {
        var jsonData = $.parseJSON(data)['annotations'];
        var idx = 0;
        var currentLabels = null;
        _frameAnnotations.length = 0;
        for (var i = 0; i < jsonData.length; i++) {
            var obj = jsonData[i];
            if (obj != null) {
                var annos = {}
                annos.background = "";
                annos.objects = []
                for (var annotation of obj) {
                    var width = annotation.w;
                    var height = annotation.h;
                    var x = annotation.x;
                    var y = annotation.y;
                    var cl = annotation.label.class;
                    var st = annotation.label.state;
                    var cmt = annotation.label.comment;
                    annos.objects.push(this.metaToObj(x, y, width, height, cl, st, cmt));
                }
                _frameAnnotations[i] = annos;
            }
        }
        _canvas.renderAll();
        this.loadFrame(1);
        this.startSyncRoutine();
    }

    this.startSyncRoutine = function () {
        var self = this;
        _syncRoutine = setInterval(function () {
            self.syncWithServer();
        }, 60000)
    }

    this.syncWithServer = function () {
        if (_autosave) {
            if (_writeMode) {
                this.saveCurrentFrame();
            }
            var self = this;
            var synced = _annotationAdapter.saveVideoAnnotations(true)
            var date = new Date();
            console.log("autosave at: " + date + " successful: " + synced);
        }
    }


    this.drawAnnotations = function (data, copy = false) {
        if (copy) {
            return;
        }
        if (data == null) {
            this.clearCanvas();
            return;
        }
        try {
            var jsonData = $.parseJSON(data);
            var currentLabels = this.getObjects();
            this.clearCanvas();
            for (var i = 0, entry; entry = jsonData[i]; i++) {
                var transform = entry['transform'];
                var x = transform['x'];
                var y = transform['y'];
                var height = transform['h'] - 1;
                var width = transform['w'] - 1;
                var klass = entry['class'];
                var state = entry['state'];
                var comment = entry['comment']
                var lbl = new Label(klass, state, comment);
                this.addAnnoation(lbl, x, y, width, height);
            }
            _canvas.setActiveObject(_canvas.item(0));
        } catch (e) {
            //console.log(e);
            return;
            //entry not found
        }
        $('#class_input').focus();

    }

    this.reset = function () {
        var originPoint = new fabric.Point(0, 0);
        _canvas.setZoom(1);
        _canvas.absolutePan(originPoint);
    }

    this.zoomToPoint = function (x, y, value = 0.1) {
        var point = new fabric.Point(x, y);
        var zoom = _canvas.getZoom();
        zoomvalue = zoom + value < 1 ? 1 : zoom + value;
        _canvas.zoomToPoint(point, zoomvalue)
    }

    this.relativePan = function (x, y) {
        var delta = new fabric.Point(x, y);
        _canvas.relativePan(delta);
    }

    this.frameEmpty = function (frame) {
        var cf = _frameAnnotations[frame]
        return this.annotationEmpty(cf);
    }

    this.annotationEmpty = function (annotation) {
        if (annotation == null || annotation.objects.length == 0) {
            return true;
        }
        return false;
    }




    this.writeFrames = function (startFrame, delta) {
        var jsonData = _canvas.toJSON();
        var absDelta = Math.abs(delta);
        //write frame(s)
        if (absDelta <= 1) {
            _frameAnnotations[startFrame] = jsonData;
        } else {
            if (delta > 0) {
                for (var i = startFrame; i < startFrame + delta; i++) {
                    _frameAnnotations[i] = jsonData;
                }
            } else {
                for (var i = startFrame - delta + 1; i <= startFrame; i++) {
                    _frameAnnotations[i] = jsonData;
                }
            }
        }
    }

    this.loadFrame = function (frame) {
        _currentFrame = frame;
        _canvas.loadFromJSON(_frameAnnotations[frame]
            , _canvas.renderAll.bind(_canvas)
            , function (o, object) { });
    }

    this.saveCurrentFrame = function () {
        if (_writeMode) {
            _frameAnnotations[_frameAnnotations] = _canvas.toJSON();
        }
    }

    this.syncAnnotation = function (frame, newFrame) {
        //write frame if changes occured and in write mode
        if (_writeMode) {
            //fill frames if delta not bigger than stepSize
            var delta = newFrame - frame;
            //var absDelta = Math.abs(delta);
            this.writeFrames(frame, delta);
        }

        //load annotation for new Frame if not propagating
        if (frame != newFrame) {
            if (!_propagate) {
                if (this.frameEmpty(newFrame)) {
                    _canvas.clear();
                } else {
                    this.loadFrame(newFrame);
                }
            }
        }
    }

    this.showCache = function () {
        console.log(_frameAnnotations);
    }

    this.setCopyMode = function (value) {
        _copyMode = value;
        if (value) {
            $('#noncopy_nav_btns').hide();
            $('#copy_nav_btns').show();
        } else {
            $('#noncopy_nav_btns').show();
            $('#copy_nav_btns').hide();
        }
    }

    this.toggleCopyMode = function () {
        this.setCopyMode(!_copyMode);
    }

    this.setOverwrite = function (value) {
        _writeMode = value;
    }

    this.setPlay = function (value) {
        _playing = value;
    }

    _canvas.selection = false //disable group selection
    _canvas.uniScaleTransform = true;
    _canvas.on({
        'object:moving': this.updateControls,
        'object:scaling': this.updateControls,
        'object:selected': this.onObjectSelected,
        'selection:cleared': this.clearControls
    });

    _canvas.on("object:scaling", function (e) {
        var target = e.target;
        if (!target || target.type !== 'anRect') {
            return;
        }
        var sX = target.scaleX;
        var sY = target.scaleY;
        target.width *= sX;
        target.height *= sY;
        target.scaleX = 1;
        target.scaleY = 1;
    });

    this.prettyPrintAnno = function (frame) {
        var metaObjs = this.objectsToMeta(_frameAnnotations[frame]);
        var result = []
        for (var mo of metaObjs) {
            var prettyObj = $.extend(true, {}, mo);
            var cl = _classes[mo.label.class].name;
            var st = _classes[mo.label.class].states[mo.label.state];
            if (st == null) {
                st = "Undefined";
            }
            var lbl = new Label(cl, st, mo.label.comment);
            prettyObj.label = lbl;
            result.push(prettyObj);
        }
        return JSON.stringify(result);
    }

    this.exportCSV = function () {
        if (_frameAnnotations.length > 2) {
            var self = this;
            var csvContent = "";
            var from = 1;
            var to = null;
            var currentAnno = this.prettyPrintAnno(from);
            var csvContent = "";
            for (var i = 1; i < _frameAnnotations.length; i++) {
                if (this.framesEqual(from, i)) {
                    to = i;
                    if (i == _frameAnnotations.length - 1) {
                        csvContent += from + ";" + to + ";" + currentAnno + "\n";
                    }
                } else {
                    csvContent += from + ";" + to + ";" + currentAnno + "\n";
                    currentAnno = this.prettyPrintAnno(i);;
                    from = i;
                    to = i;
                }
            }
            /*_frameAnnotations.forEach(function (object, index) {
                dataString = index + ";" + JSON.stringify(self.objectsToMeta(object))
                csvContent += index < _frameAnnotations.length ? dataString + "\n" : dataString;
            });*/
            var encodedUri = encodeURI(csvContent);
            var a = document.createElement('a');
            a.href = 'data:attachment/csv,' + encodedUri;
            a.target = '_blank';
            a.download = _videoLoader.vName + '_export_' + Date.now() + '.csv';
            document.body.appendChild(a);
            a.click();
        }
    }
}

 /*this.initVideoAnnotationfromDB = function (response) {
        var idx = 0;
        var currentLabels = null;
        for (var obj in response) {
            var annos = {}
            annos.background = "";
            annos.objects = []
            var annotations = $.parseJSON(response[obj]);
            for (var annotation of annotations) {

                annos.objects.push(this.metaToRect(annotation));
            }
            _keyFrameAnnotationCache[obj] = annos;
        }
        this.expandFromKeyFrameCache();
        _canvas.renderAll();
        this.startSyncRoutine();
    }

    this.expandFromKeyFrameCache = function () {
        _keyFrames.length = 0;
        _keyFrames = Object.keys(_keyFrameAnnotationCache);
        var maxFrame = _videoLoader.getMaxFrames();
        var prevKeyFrame = 1;
        for (var i = 0; i < _keyFrames.length; i++) {
            var curKF = _keyFrames[i];
            var nextKF = i + 1 == _keyFrames.length ? maxFrame : _keyFrames[i + 1];
            for (var j = parseInt(curKF); j < nextKF; j++) {

                var ann = _keyFrameAnnotationCache[curKF];
                _frameAnnotations[j] = ann;
            }
        }
    }*/


/*try {
        var jsonData = $.parseJSON(data);
        _frameAnnotations.length = 0;
        _frameAnnotations = jsonData['annotations'];
        //this.extractKeyFrames();
        this.loadFrame(1);
        _canvas.renderAll();
        this.startSyncRoutine();
    }*/


    /*this.startSyncRoutine = function () {
        var self = this;
        _syncRoutine = setInterval(function () {
            //compute delta
            var kfcKeys = Object.keys(_keyFrameAnnotationCache);
            var added = _keyFrames.filter(x => kfcKeys.indexOf("" + x) == -1);
            var removed = kfcKeys.filter(x => _keyFrames.indexOf(parseInt(x)) == -1);
            //sync with cache
            for (var r of removed) {
                delete (_keyFrameAnnotationCache[r]);
            }
            var updated = [];
            kfcKeys = Object.keys(_keyFrameAnnotationCache);
            for (var k of kfcKeys) {
                var intk = parseInt(k);
                if (!self.annotationsEqual(_frameAnnotations[intk], _keyFrameAnnotationCache[k])) {
                    _keyFrameAnnotationCache[k] = Object.assign({}, _frameAnnotations[intk]);
                    updated.push(intk);
                }
            }
            for (var a of added) {
                if (self.frameEmpty(a)) {
                    _keyFrameAnnotationCache[a] = undefined
                } else {
                    _keyFrameAnnotationCache[a] = Object.assign({}, _frameAnnotations[a]);
                }
            }
    
            //perform sync
            if (added.length > 0 || removed.length > 0 || updated.length > 0) {
                var updateIndices = added.concat(updated);
                var updateData = {}
                for (var i of updateIndices) {
                    updateData[i] = self.objectsToMeta(_frameAnnotations[i]);
                }
                _annotationAdapter.updateVideoAnnotations(updateData, removed);
    
            }
    
        }, 5000)
    }*/

      /*this.isKeyFrame = function (frame) {
        var prevFrame = _frameAnnotations[frame - 1];
        var nextFrame = _frameAnnotations[frame + 1];
        if (prevFrame == null) {
            return true;
        }
        return (!this.framesEqual(frame, frame - 1) ||
            (nextFrame != null && !this.framesEqual(frame, frame + 1)))
    }

    this.checkKeyFrame = function (frame) {
        var keyframeIdx = $.inArray(frame, _keyFrames)
        if (this.isKeyFrame(frame)) {
            if (keyframeIdx == -1) {
                _keyFrames.push(frame);
            }
        }
        else {
            if (keyframeIdx != -1) {
                _keyFrames.splice(keyframeIdx, 1);
            }
        }
    }

    this.extractKeyFrames = function () {
        _keyFrames.length = 0;
        _frameAnnotations.forEach((v, i) => {
            if (i > 0 && this.isKeyFrame(i)) {
                _keyFrames.push(i);
            }
        });
        return _keyFrames;
    }*/




