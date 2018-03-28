$(function () {
    _labelController.clearControls();

    $('#imgSlider').on('input', function () {
        var sliderVal = $(this).val();
        _labelController.toggleWrite(false);
        //$('#frame-input').val(sliderVal);
        //$('#frame-input').trigger('input');
        _videoLoader.jumpToFrame(sliderVal);
    });

    /*$('#frame-input').on('wheel', function (e) {
        e.preventDefault();
        var delta = -Math.sign(e.originalEvent.wheelDelta);
        _annotationAdapter.updateAnnotation(delta);
        /*var frame = $(this).val();
        $(this).val(parseInt(frame)+delta);
        $(this).trigger('input');
    });*/

    $('#frame-input').on('change', function () {
        //console.log("triggered");
        _labelController.toggleWrite(false);
        var frame = $(this).val();
        if (_mode == "video") {
            _videoLoader.jumpToFrame(frame);
        }
        $('#imgSlider').val(frame);
    });

    $('#frame-input').on('input', function () {
        //console.log("triggered");
        var frame = $(this).val();
        if (_mode == "video") {

        } else {
            var currentFrame = _mediaLoader.getCurrentFrame();
            var offset = frame - currentFrame;
            _annotationAdapter.updateAnnotation(offset);
        }
    });

    $('#folder_input').change(function () {
        var files = $(this).prop("files");
        var path = files[0].webkitRelativePath;
        var root = path.split("/")[0];
        _mediaLoader.init(files, root);
        _annotationAdapter.getAnnotation(0);
    });

    $('#video_input').change(function () {
        var file = $(this).prop("files")[0];
        _videoLoader.loadVideo(file);
    });


    $('#currentImg').load(function () {
        var img = document.getElementById("currentImg");
        _labelController.setBackground(img);
    });

    $('#bar-toggle').click(function () {
        var hidden = $(this).attr('data-hidden');
        if (hidden == 'true') {
            $(this).attr('data-hidden', 'false');
            $(this).html('<span class="glyphicon glyphicon-triangle-bottom" aria-hidden="true"></span> Hide Progress Bar')
        } else {
            $(this).attr('data-hidden', 'true');
            $(this).html('<span class="glyphicon glyphicon-triangle-top" aria-hidden="true"></span> Show Progress Bar')
        }
    });

    $('#add_label_btn').click(function () {
        var klass = $('#class_input').val();
        var state = $('#state_input').val();
        _labelController.addAnnoationWithClassAndState(klass, state);
    });

    $('#delete_label_btn').click(function () {
        _labelController.deleteCurrentAnnotation();
    });

    $('#sf-btn').click(function () {
        //_annotationAdapter.updateAnnotation(1);
        _videoLoader.nextFrame();
    });

    $('#csf-btn').click(function () {
        //_annotationAdapter.updateAnnotation(1, true);
        _videoLoader.nextFrame();

    });

    $('#sb-btn').click(function () {
        //_annotationAdapter.updateAnnotation(-1);
        _videoLoader.prevFrame();
    });

    $('#csb-btn').click(function () {
        //_annotationAdapter.updateAnnotation(-1, true);
        _videoLoader.prevFrame();
    });

    $('#play-btn').click(function () {
        nIntervId = setInterval(function () {
            _mediaLoader.updateIdx(1);
            _mediaLoader.loadFrame();
            current = current + 1;
        }, 100);
    });

    $('#comment_input').on('input', function () {
        _labelController.updateLabelComment($(this).val());
    });

    $('#class_input').on('change', function () {
        _labelController.updateLabelClass($(this).val());
    });

    $('#state_input').on('change', function () {
        //console.log("input");
        _labelController.updateLabelState($(this).val());
    });

    $('#canvas-panel').on('wheel', function (e) {
        if (e.shiftKey) {
            e.preventDefault();
            var delta = -Math.sign(e.originalEvent.wheelDelta);
            var x = e.originalEvent.offsetX;
            var y = e.originalEvent.offsetY;
            _labelController.zoomToPoint(x, y, delta * 0.1);
        }
    });

    $('#canvas-panel').on('wheel', function (e) {
        if (e.shiftKey) {
            e.preventDefault();
            var delta = -Math.sign(e.originalEvent.wheelDelta);
            var x = e.originalEvent.offsetX;
            var y = e.originalEvent.offsetY;
            _labelController.zoomToPoint(x, y, delta * 0.1);
        }
    });

    //ToDo: refactor this into label_controller class
    var panning = false;
    $('#canvas-panel').on('mouseup', function (e) {
        panning = false;
    });
    $('#canvas-panel').on('mouseout', function (e) {
        panning = false;
    });
    $('#canvas-panel').on('mousedown', function (e) {
        panning = true;
    });
    $('#canvas-panel').on('mousemove', function (e) {
        if (panning && e && e.originalEvent && e.shiftKey) {
            e.preventDefault();
            var x = e.originalEvent.movementX;
            var y = e.originalEvent.movementY;
            _labelController.relativePan(x, y);
        }
    });



    $('#proj_sel').on('change', function () {
        _annotationAdapter.updateClasses($(this).val());
    });


    $('#step-size').on('input', function () {
        _videoLoader.stepSize = $(this).val();
    });

    $('#save-file').on('click', function () {
        _labelController.saveCurrentFrame();
        _annotationAdapter.saveVideoAnnotations();
    });

    $('#export-button').on('click', function () {
        _labelController.exportCSV();
    });

});


