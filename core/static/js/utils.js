/**
 * Created by davit on 2/15/16.
 */
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define([], factory);
    } else {
        // Browser globals
        root.utils = factory(root.b);
    }
}(this, function () {
    'use strict';
    
    function sendForm(form, callback, on_err, url) {
        var formData = new FormData(form);
        var sendUrl = !!url ? url : form.getAttribute('action');
        
        var xhr = new XMLHttpRequest();
        
        xhr.open("POST", sendUrl);
        
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        
        xhr.onreadystatechange = function() { // (3)
          if (xhr.readyState != 4) return;
          if (xhr.status != 200 && xhr.status != 201) {
              !!on_err && on_err(form, xhr.responseText)
          } else {
              callback && callback(xhr.responseText)
          }
        };
        xhr.send(formData);
    }
    return {
        sendForm: sendForm
    };
}));