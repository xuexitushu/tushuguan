var _busy = false
var _mediaLoader = new MediaLoader('#currentImg');
var _videoLoader = new VideoLoader('#currentVideo', '#c');
var _labelController = new LabelController('c');
var _annotationAdapter = new AnnotationAdapter();
var _mode = "video";




//operations to perform after load
$(function () {
    var prs = $('#proj_sel');
    var prdefault = prs.data('default');
    prs.val(prdefault);
    _annotationAdapter.updateClasses(prdefault);
    console.log("set default project to: " + prdefault);
});


