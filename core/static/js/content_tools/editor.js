


window.addEventListener('load', function() {
    var update_url = document.getElementById('page_update_url').value;
    var picture_url = document.getElementById('picture_add_url').value;

    function imageUploader(dialog) {
        var image, xhr, xhrComplete, xhrProgress;

        dialog.bind('imageUploader.save', function () {
            dialog.save(
                        image.url,
                        image.size);
        });
        dialog.bind('imageUploader.cancelUpload', function () {
            // Cancel the current upload

            // Stop the upload
            if (xhr) {
                xhr.upload.removeEventListener('progress', xhrProgress);
                xhr.removeEventListener('readystatechange', xhrComplete);
                xhr.abort();
            }

            // Set the dialog to empty
            dialog.state('empty');
        });

        dialog.bind('imageUploader.clear', function () {
            // Clear the current image
            dialog.clear();
            image = null;
        });

        dialog.bind('imageUploader.fileReady', function (file) {
            // Upload a file to the server
            var formData;

            // Define functions to handle upload progress and completion
            xhrProgress = function (ev) {
                // Set the progress for the upload
                dialog.progress((ev.loaded / ev.total) * 100);
            };

            xhrComplete = function (ev) {
                var response;

                // Check the request is complete
                if (ev.target.readyState != 4) {
                    return;
                }

                // Clear the request
                xhr = null;
                xhrProgress = null;
                xhrComplete = null;

                // Handle the result of the upload
                if (parseInt(ev.target.status) == 200) {
                    // Unpack the response (from JSON)
                    response = JSON.parse(ev.target.responseText);

                    // Store the image details
                    image = {
                        size: response.size,
                        url: response.url
                    };

                    // Populate the dialog
                    dialog.populate(image.url, image.size);

                } else {
                    // The request failed, notify the user
                    new ContentTools.FlashUI('no');
                }
            };

            // Set the dialog state to uploading and reset the progress bar to 0
            dialog.state('uploading');
            dialog.progress(0);

            // Build the form data to post to the server
            formData = new FormData();
            formData.append('picture', file);

            // Make the request
            xhr = new XMLHttpRequest();
            xhr.upload.addEventListener('progress', xhrProgress);
            xhr.addEventListener('readystatechange', xhrComplete);
            xhr.open('POST', picture_url, true);
            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
            xhr.send(formData);
        });

        function rotateImage(direction) {
            // Request a rotated version of the image from the server
            var formData;

            // Define a function to handle the request completion
            xhrComplete = function (ev) {
                var response;

                // Check the request is complete
                if (ev.target.readyState != 4) {
                    return;
                }

                // Clear the request
                xhr = null
                xhrComplete = null

                // Free the dialog from its busy state
                dialog.busy(false);

                // Handle the result of the rotation
                if (parseInt(ev.target.status) == 200) {
                    // Unpack the response (from JSON)
                    response = JSON.parse(ev.target.responseText);

                    // Store the image details (use fake param to force refresh)
                    image = {
                        size: response.size,
                        url: response.url + '?_ignore=' + Date.now()
                        };

                    // Populate the dialog
                    dialog.populate(image.url, image.size);

                } else {
                    // The request failed, notify the user
                    new ContentTools.FlashUI('no');
                }
            }

            // Set the dialog to busy while the rotate is performed
            dialog.busy(true);

            // Build the form data to post to the server
            formData = new FormData();
            formData.append('url', image.url);
            formData.append('direction', direction);

            // Make the request
            xhr = new XMLHttpRequest();
            xhr.addEventListener('readystatechange', xhrComplete);
            xhr.open('POST', '/rotate-image', true);
            xhr.send(formData);
        }

        dialog.bind('imageUploader.rotateCCW', function () {
            rotateImage('CCW');
        });

        dialog.bind('imageUploader.rotateCW', function () {
            rotateImage('CW');
        });


    }
    ContentTools.IMAGE_UPLOADER = imageUploader;
    var editor;
    editor = ContentTools.EditorApp.get();
    editor.init('*[data-editable]', 'data-name');

    editor.bind('save', function (regions) {
        var name, payload, xhr;

        // Set the editor as busy while we save our changes
        this.busy(true);
        var send = false;
        // Collect the contents of each region into a FormData instance
        payload = new FormData();

        for (name in regions) {
            if (regions.hasOwnProperty(name)) {
                send = true;
                payload.append('content_text', regions[name]);
                payload.append('slug', name);
            }
        }
        if(!send)
        {
            new ContentTools.FlashUI('ok');
            return;
        }

        // Send the update content to the server to be saved
        function onStateChange(ev) {
            // Check if the request is finished
            if (ev.target.readyState == 4) {
                editor.busy(false);
                if (ev.target.status == '200') {
                    // Save was successful, notify the user with a flash
                    new ContentTools.FlashUI('ok');
                } else {
                    // Save failed, notify the user with a flash
                    new ContentTools.FlashUI('no');
                }
            }
        }

        xhr = new XMLHttpRequest();
        xhr.addEventListener('readystatechange', onStateChange);
        xhr.open('POST', update_url);
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        xhr.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
        xhr.send(payload);
    });
});