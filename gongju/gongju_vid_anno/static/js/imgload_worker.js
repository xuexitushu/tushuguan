importScripts("../vendor/tiffjs/tiff.min.js");
Tiff.initialize({ TOTAL_MEMORY: 100000000 });

onmessage = function (event) {
    console.log("received message");
    var data = event.data.blob;
    var rd = new FileReaderSync();
    var buffer = rd.readAsArrayBuffer(data);
    //console.log(buffer);
    var tiff = new Tiff({ buffer: buffer });
    var image = tiff.readRGBAImage();
    self.postMessage({ image: image, width: tiff.width(), height: tiff.height(), index: event.data.index }, [image]);
};


/*onmessage = function(e){
    console.log("Message Received");
}*/



