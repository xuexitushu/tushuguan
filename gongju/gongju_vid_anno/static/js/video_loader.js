class VideoLoader {
    constructor(vElement, cElement, fps = 15) {
        this.slider = $('#imgSlider');
        this.frameInput = $('#frame-input');
        this.stepInput = $('#step-size');
        this.statusCtx = $('#status-display')[0].getContext('2d');
        this.fps = fps;
        this.vElement = vElement;
        this.cElement = cElement;
        this.ctx = $(this.cElement)[0].getContext('2d');
        this.c = $(this.cElement)[0];
        this.v = $(this.vElement)[0];
        this.seeking = false;
        this.loaded = false;
        this.vWidth = 0;
        this.vHeight = 0;
        this.vDur = 0;
        this.canvasSync = null;
        this.searchingForFPS = false;
        this.frame = 1;
        this.lastUpdate = Date.now();
        this.syncTimer = 0;
        this.syncInterval = 5000;
        this.stepSize = 1;
        this.vName = "";
        this.currentKeyFrames = [];
    }
    getName() {
        return this.vName;
    }

    loadVideo(video) {
        this.vName = video.name;
        this.statusCtx.fillText("TEST", 0, 0);
        var self = this;
        var URL = window.URL || window.webkitURL;
        var fileURL = URL.createObjectURL(video);
        $(this.vElement).attr('src', fileURL);
        /*$(this.vElement).on('timeupdate', function () {
            self.frameInput.val(self.timeToFrame(self.v.currentTime));
        })*/
        $(this.vElement).on('loadeddata', function () {
            $('#raw_file_name').html("<p>" + self.vName + "</p>");
            self.vWidth = this.videoWidth;
            self.vHeight = this.videoHeight;
            self.vDur = this.duration;
            //init slider
            self.slider.attr('max', self.timeToFrame(self.vDur));
            self.slider.attr('min', 1);
            self.frameInput.val(1);
            console.log("Video loaded:");
            console.log("w: " + self.vWidth);
            console.log("h: " + self.vHeight);
            console.log("d: " + self.vDur);
            //_annotationAdapter.loadVideoAnnotations();
            _annotationAdapter.initAnnotation(self.vName, 1, true);
            _labelController.initVideo(self.vWidth, self.vHeight, this);

        })

        //sync
        /*setInterval(function () {
            //var newFrame = Math.ceil(self.v.currentTime * self.fps);
            self.update();
        }, 10)*/
    }

    setStepSize(newSize) {
        var newSize = newSize > 1 ? newSize : 1;
        this.stepSize = newSize;
        this.stepInput.val(this.stepSize);
    }

    update() {
        var newFrame = this.timeToFrame(this.v.currentTime);
        if (newFrame == 0) newFrame = 1;
        if (this.frame != newFrame) {
            _labelController.syncAnnotation(this.frame, newFrame);
            this.frame = newFrame;
            this.statusCtx.fillStyle = "#00EEEE";
            this.statusCtx.font = "bold 20px Arial";
            this.statusCtx.clearRect(0, 0, 150, 100);
            this.statusCtx.fillText(newFrame, 0, 20)
            this.slider.val(newFrame);
            if (this.v.playbackRate == 1) {
                this.frameInput.val(newFrame);
            }
        }
    }

    play() {
        this.v.play();
    }

    pause() {
        this.v.pause();
    }

    reset() {
        this.v.currentTime = 0;
    }

    setRate(rate) {
        this.v.playbackRate = rate;

    }

    getLength() {
        return this.v.duration;
    }

    getMaxFrames() {
        return this.timeToFrame(this.getLength());
    }

    /*findFPS() {
        var self = this;
        this.cacheFrames = []
        this.v.currentTime = 0;
        this.searchingForFPS = true;
        this.v.onseeked = function () {
            self.ctx.drawImage(self.v, 0, 0, self.vWidth, self.vHeight);
            self.cacheFrames.push(self.c.toDataURL());
            console.log(self.c.toDataURL());
        }
        for (var i = 0; i < 60; i++) {
            this.v.currentTime += 1 / 60;
        }
    }*/

    nextFrame() {

        var frame = parseInt(this.frame)
        this.jumpToFrame(frame + parseInt(this.stepSize));

    }

    prevFrame() {
        var frame = parseInt(this.frame)
        this.jumpToFrame(frame - parseInt(this.stepSize));
    }

    jumpToFrame(frame) {
        var newTime = this.frameToTime(frame);
        if (newTime >= 0 && newTime <= this.v.duration) {
            this.v.currentTime = this.frameToTime(frame);
            this.update();
        } else {
            console.log("Frame Index out of bounds");
        }
    }

    frameToTime(frame) {
        var time = frame * 1.0 / this.fps;
        return time;
    }

    timeToFrame(time) {
        var frameFloat = time * this.fps;
        return Math.ceil(frameFloat.toFixed(3));
    }

    draw() {
        //this.v.currentTime += 5;
        this.ctx.drawImage(this.v, 0, 0, 800, 600);
    }
}



