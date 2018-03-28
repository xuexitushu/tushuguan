function ImageRequest(file) {
    var file;
    var time;
    this.file = file;
    this.time = Date.now();
}

function MediaLoader(imgElement) {
    var _imgSrcFiles = [];
    var _imgDataCache = [];
    var _currentFrameIdx = 0;
    var _folderName = "";
    var _imgElement = imgElement;
    var _busyloading = false;
    var _progressbar = $('#imgSlider');
    var _fileLabel = $('#raw_file_name');
    var _fileNameLabel = $('#frame_name');
    var _cachedRequest = null;
    var _self = this;

    this.lexSort = function(aFile,bFile){
        var a = aFile.name;
        var b= bFile.name;
        if(a.length != b.length){
            return a.length-b.length;
        } else {
            for (var i=0; i<a.length; i++){
                if(a[i] != b[i]){
                    return a[i] - b[i]
                }
            }
        }
        return 1;
    }

    this.init = function (files, root) {
        _currentFrameIdx = 0;
        _imgSrcFiles.length = 0;
        _folderName = root;
        for (var i = 0, f; f = files[i]; i++) {
            if (f.type.match('image.*')) {
                _imgSrcFiles.push(f);
            }
        }
        //sort files
        //console.log(_imgSrcFiles[0].name);
        _imgSrcFiles.sort(_self.lexSort);
        //init slider
        _progressbar.attr('max', _imgSrcFiles.length - 1);
        _progressbar.val(0);


        var projectId = $('#proj_sel').val();
        _annotationAdapter.initAnnotation(_folderName, projectId);
        _annotationAdapter.getAnnotatedFrames(_folderName, projectId);
        _fileLabel.html("<b>"+_folderName+"</b>");
    }

    this.geteInfo = function () {
        return { 'current': _currentFrameIdx, 'total': _imgSrcFiles.length }
    }

    this.getCurrentFrame = function () {
        return _currentFrameIdx;
    }

    this.getCurrentFrameName = function () {
        if (_imgSrcFiles[_currentFrameIdx] != null) {
            return _imgSrcFiles[_currentFrameIdx]['name'];
        } else {
            return 0;
        }
        //console.log(_imgSrcFiles[_currentFrameIdx]);
    }

    this.loadFrame = function () {
        if (_imgSrcFiles.length > 0) {
            var imageFile = _imgSrcFiles[_currentFrameIdx];
            this.loadImage(imageFile);
        } else {
            console.log("no frames loaded")
        }
    }

    this.loadImage = function (imageFile) {
        if (_busyloading) {
            console.log("busy...");
            return false;
        } else {
            _busyloading = true;
            rd = new FileReader();
            rd.fileName = imageFile.name;
            rd.onload = function (e) {
                $(_imgElement).attr('src', rd.result);
                _busyloading = false;
                if(rd.fileName != _imgSrcFiles[_currentFrameIdx].name){
                    console.log("async detected!");
                    _self.loadFrame();
                }
            }
            rd.readAsDataURL(imageFile);
            _fileNameLabel.html(imageFile.name);
            return true;
        }
    }

    this.updateIdx = function (val) {
        var newIdx = _currentFrameIdx + val;
        var max = _imgSrcFiles.length - 1;
        _currentFrameIdx = newIdx < 0 ? 0 : newIdx > max ? max : newIdx;
        return _currentFrameIdx
    }
}
