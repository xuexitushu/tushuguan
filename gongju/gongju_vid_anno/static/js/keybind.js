var _playing = false

$(document).keydown(function (e) {
    //numpad:
    // [103][104][105]
    // [100][101][102]
    // [ 97][ 98][ 99]
    /*if (e.shiftKey) {
        console.log("shift key");
        console.log(e.which);
    }*/
    switch (e.which) {
        case 97: //numpad1:save annotation automatically when the button for next frame is in yellow
            e.preventDefault();
            _labelController.toggleWrite();
            break;
        case 98: //np2
            e.preventDefault();
            _labelController.togglePropagation();
            break;
        case 99: //np3
            e.preventDefault();

            break;

        case 100: //np4
            e.preventDefault();
            _videoLoader.prevFrame();
            break;

        case 101: // np5
            e.preventDefault();
            _videoLoader.setStepSize(_videoLoader.stepSize - 1);

            break;

        case 102: // np6
            e.preventDefault();
            _videoLoader.nextFrame();
            break;

        case 103: // np7
            e.preventDefault();
            if (e.ctrlKey) {
                $("#class_input > option:selected")
                    .prop("selected", false)
                    .prev()
                    .prop("selected", true);
                $("#class_input").trigger('change');
            } else {
                $("#class_input > option:selected")
                    .prop("selected", false)
                    .next()
                    .prop("selected", true);
                $("#class_input").trigger('change');
            }
            break;

        case 104: // np8
            e.preventDefault();
            _videoLoader.setStepSize(_videoLoader.stepSize + 1);
            break;

        case 105: // np9
            e.preventDefault();
            if (e.ctrlKey) {
                $("#state_input > option:selected")
                    .prop("selected", false)
                    .prev()
                    .prop("selected", true);
                $("#state_input").trigger('change');
            } else {
                $("#state_input > option:selected")
                    .prop("selected", false)
                    .next()
                    .prop("selected", true);
                $("#state_input").trigger('change');
            }
            break;


        /*case 32: //space
            if (_playing) {
                _videoLoader.pause();
                _playing = false;
            } else {
                _videoLoader.play();
                _playing = true;
            }
            console.log("play");
            break;

        case 77: //backspace
            console.log("m");
            e.preventDefault();
            _videoLoader.setRate(12);
            break;

        case 78: //backspace
            console.log("n");
            e.preventDefault();
            _videoLoader.setRate(1);
            break;*/

        case 36: //pos1
            e.preventDefault();
            _labelController.reset();
            break;
        case 107: // numpad plus
            e.preventDefault();
            e.stopPropagation();
            _labelController.showCache();
            _annotationAdapter.updateVideoAnnotations();
            break;

        case 109: // numpad minus
            e.preventDefault();
            e.stopPropagation();
            _videoLoader.reset();
            break;

        case 80: //P
            e.preventDefault();
            _labelController.toggleCopyMode();
            break;

        case 18: //alt
            e.preventDefault();
            $('#noncopy_nav_btns').hide();
            $('#copy_nav_btns').show();
            break;

        case 45: // ins
            $('#add_label_btn').click();
            break;

        case 46: // del
            $('#delete_label_btn').click();
            break;

        case 89: //x
            if (e.ctrlKey) {
                $("#class_input > option:selected")
                    .prop("selected", false)
                    .next()
                    .prop("selected", true);
                $("#class_input").trigger('change');
            }
            break;

        case 88: //y
            if (e.ctrlKey) {
                $("#stat_input > option:selected")
                    .prop("selected", false)
                    .next()
                    .prop("selected", true);
                $("#class_input").trigger('change');

            }
            break;

        case 67: //c
            if (e.ctrlKey) {
                $('#comment_input').focus();
            }
            break;

        default: return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
});

$(document).keyup(function (e) {
    switch (e.which) {

        case 18: //alt
            $('#noncopy_nav_btns').show();
            $('#copy_nav_btns').hide();
            break;

        default: return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
});

#annotation..
//This class servers as adapter between Frontend and Backend for the exchange of annotation related information

function AnnotationAdapter() {
    var _busy = false;
    var _rawDataID = null;
    var _self = this;
    var _dataList = $('#ticks');

    var _classes = {};



    this.updateStates = function (class_id, countdown) {
        $.ajax({
            url: '/get_states',
            type: 'POST',
            data: JSON.stringify({ class_id: class_id }),
            contentType: 'application/json;charset=UTF-8',
            success: function (response) {
                respJson = $.parseJSON(response);
                _classes[class_id].states = respJson;
                if (countdown == 0) {
                    _labelController.initInput(_classes);
                }
            }
        });
    }

    this.updateClasses = function (projectId) {
        _classes = {}
        $.ajax({
            url: '/get_classes',
            type: 'POST',
            data: JSON.stringify({ project_id: projectId }),
            contentType: 'application/json;charset=UTF-8',
            success: function (response) {
                respJson = $.parseJSON(response);
                var clsCount = Object.keys(respJson).length;
                for (var key in respJson) {
                    clsCount--;
                    _classes[key] = {}
                    _classes[key].name = respJson[key]
                    _self.updateStates(key, clsCount)
                }
            }
        });
    }



    this.getAnnotation = function (offset, copy = false) {
        if (_busy == false) {
            _busy = true;
            var nextFrame = _mediaLoader.updateIdx(offset);
            sendData = {
                'next_frame': nextFrame
            };
            sendData = JSON.stringify(sendData);
            $.ajax({
                url: '/get_annotation',
                data: sendData,
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                type: 'POST',
                success: function (response) {
                    _mediaLoader.loadFrame();
                    _labelController.drawAnnotations(response, copy);
                    $('#frame-input').val(nextFrame);
                    _busy = false;
                },
                error: function (error) {
                    console.log(error);
                    _busy = false;
                }
            });
        }
    }

    this.updateVideoAnnotations = function (data) {
        if (_busy == false) {
            _busy = true;
            var cachedFrames = _labelController.getCachedFrames();
            var sendData = JSON.stringify(data);
            $.ajax({
                url: '/update_video_annotations',
                data: sendData,
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                type: 'POST',
                success: function (response) {
                    _busy = false;
                },
                error: function (error) {
                    console.log(error);
                    _busy = false;
                }
            });
            return true;
        } else {
            return false;
        }
    }

    this.saveVideoAnnotations = function (cache = false) {
        if (_busy == false) {
            _busy = true;
            $('#save-file').prop('disabled', true);
            var cachedFrames = _labelController.exportMetaData();
            var name = _videoLoader.getName();
            if (cache) name = name + '_cache';
            var send = {
                name: name,
                annotations: cachedFrames
            }
            sendData = JSON.stringify(send);
            $.ajax({
                url: '/save_video_annotations',
                data: sendData,
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                type: 'POST',
                success: function (response) {
                    $('#save-file').prop('disabled', false);
                    _busy = false;
                },
                error: function (error) {
                    $('#save-file').prop('disabled', false);
                    _busy = false;
                }
            });
        }
    }

    this.loadVideoAnnotations = function () {
        if (_busy == false) {
            _busy = true;
            var send = {
                name: _videoLoader.getName(),

            }
            sendData = JSON.stringify(send);
            $.ajax({
                url: '/load_video_annotations',
                data: sendData,
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                type: 'POST',
                success: function (response) {
                    _labelController.initVideoAnnotation(response);
                    _busy = false;
                },
                error: function (error) {
                    console.log(error);
                    _busy = false;
                }
            });
        }
    }

    this.loadVideoAnnotationsFromDB = function () {
        if (_busy == false) {
            _busy = true;
            if (_rawDataID == null) {
                console.log("no data loaded");
                return;
            }
            sendData = { raw_data_id: _rawDataID };
            sendData = JSON.stringify(sendData);

            $.ajax({
                url: '/load_video_annotations_db',
                data: sendData,
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                type: 'POST',
                success: function (response) {
                    _labelController.initVideoAnnotationfromDB(response);
                    _busy = false;
                },
                error: function (error) {
                    console.log(error);
                    _busy = false;
                }
            });
        }
    }


    this.updateAnnotation = function (offset, copy = false) {
        if (_busy == false) {
            _busy = true;
            var annotationObjects = _labelController.getObjects();
            var currentFrame = _mediaLoader.getCurrentFrame();
            var currentFrameName = _mediaLoader.getCurrentFrameName();
            var nextFrame = _mediaLoader.updateIdx(offset);
            sendData = {
                'frame': currentFrame,
                'frame_name': currentFrameName,
                'annotation_data': annotationObjects,
                'next_frame': nextFrame
            };
            //_mediaLoader.loadFrame();
            //_labelController.drawAnnotations('[]',false);

            sendData = JSON.stringify(sendData);
            $.ajax({
                url: '/update',
                data: sendData,
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                type: 'POST',
                success: function (response) {
                    _mediaLoader.loadFrame();
                    _labelController.drawAnnotations(response, copy);
                    $('#frame-input').val(nextFrame);
                    $('#frame-input').trigger('change');
                    //
                    if (annotationObjects.length == 0) {
                        _labelController.removeTick(currentFrame);
                    } else {
                        _labelController.addTick(currentFrame);
                    }

                    _busy = false;
                },
                error: function (error) {
                    console.log(error);
                    _busy = false;
                }
            });
        }
    }

    this.getAnnotatedFrames = function () {
        if (_rawDataID == null) {
            console.log("no data loaded");
            return;
        }
        send_data = { raw_data_id: _rawDataID };
        send_data = JSON.stringify(send_data);
        $.ajax({
            url: '/get_annoated_frames',
            data: send_data,
            //dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            success: function (response) {
                var annotatedList = $.parseJSON(response);
                _labelController.initSliderTicks(annotatedList);
            },
            error: function (error) {
                console.log(response);
            }
        });
    }

    this.initAnnotation = function (name, projectId, video = false) {
        console.log("init annotation with: " + name + "," + projectId);
        send_data = { project_id: projectId, raw_data_name: name };
        send_data = JSON.stringify(send_data);
        $.ajax({
            url: '/init',
            data: send_data,
            //dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            success: function (response) {
                console.log("raw data id: " + response);
                _rawDataID = parseInt(response);
                if (!video) {
                    _self.getAnnotatedFrames();
                } else {
                    //_self.loadVideoAnnotationsFromDB();
                    _self.loadVideoAnnotations();
                }
            },
            error: function (error) {
                console.log(response);
            }
        });
    }


}


