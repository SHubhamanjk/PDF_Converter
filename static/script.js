function fileUploaded() {
    var fileInput = document.getElementById("file");
    if (fileInput.files.length > 0) {
        var file = fileInput.files[0];
        if (file.name.endsWith(".txt") || file.name.endsWith(".wav")) {
            var message = document.getElementById("uploadMessage");
            message.textContent = "File has been successfully uploaded!";
            message.style.display = "block";
            setTimeout(function() {
                message.style.display = "none";
            }, 3000);
        } else {
            alert("Please upload a .txt or .wav file");
            fileInput.value = '';
        }
    }
}
