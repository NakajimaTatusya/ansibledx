var stream;
var video;

var constraint = {
    video: {
        mandatory: {
            maxWidth: 320,
            maxHeight: 240
        }
    },
    audio: false
};

navigator.mediaDevices.getUserMedia(constraint).then(function (stream) {
    stream = stream;
    video = document.getElementById('video');
    video.src = window.URL.createObjectURL(stream);
    video.play();

    setTimeout(() => {
        var canvas = document.getElementById('canvas');
        var ctx = canvas.getContext('2d');
        var w = video.offsetWidth;
        var h = video.offsetHeight;
        canvas.setAttribute('width', w);
        canvas.setAttribute('height', h);
        ctx.drawImage(video, 0, 0, w, h);
        canvas.toBlob(function (blob) {
            var img = document.getElementById('image');
            img.src = window.URL.createObjectURL(blob);

            var request = new XMLHttpRequest();
            request.open('post', '/');
            request.setRequestHeader('X-CSRF-Token', $('meta[name="csrf-token"]').attr('content'));
            var formData = new FormData();
            formData.append('avatar[image]', blob, '<%= Time.now.strftime("%Y%m%d%H%M") %>}.jpeg');
            formData.append('avatar[uuid]', '<%= user.uuid %>');
            request.send(formData);
        }, 'image/jpeg', 0.95);
        stream.getTracks()[0].stop();
    }, 3000);
}).catch(function (error) {
    console.log('mediaDevice.getUserMedia() error' + error);
    return;
});

