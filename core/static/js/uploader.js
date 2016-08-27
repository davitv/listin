/**
 * Created by davit on 2/15/16.
 */
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define([], factory);
    } else {
        // Browser globals
        root.Uploader = factory(root.b);
    }
}(this, function () {
    'use strict';
    
    
    function getResizeInfo(file, thumbnailWidth, thumbnailHeight) {
        var info = {
            srcX: 0,
            srcY: 0,
            srcWidth: file.width,
            srcHeight: file.height
        };
        var srcRatio = file.width / file.height;
        info.optWidth = thumbnailWidth;
        info.optHeight = thumbnailHeight;
        if ((info.optWidth == null) && (info.optHeight == null)) {
          info.optWidth = info.srcWidth;
          info.optHeight = info.srcHeight;
        } else if (info.optWidth == null) {
          info.optWidth = srcRatio * info.optHeight;
        } else if (info.optHeight == null) {
          info.optHeight = (1 / srcRatio) * info.optWidth;
        }
        var trgRatio = info.optWidth / info.optHeight;
        if (file.height < info.optHeight || file.width < info.optWidth) {
          info.trgHeight = info.srcHeight;
          info.trgWidth = info.srcWidth;
        } else {
          if (srcRatio > trgRatio) {
            info.srcHeight = file.height;
            info.srcWidth = info.srcHeight * trgRatio;
          } else {
            info.srcWidth = file.width;
            info.srcHeight = info.srcWidth / trgRatio;
          }
        }
        info.srcX = (file.width - info.srcWidth) / 2;
        info.srcY = (file.height - info.srcHeight) / 2;
        return info;
    }
    function createThumbnail(file, callback, width, height) {
        var fileReader;
        fileReader = new FileReader;
        fileReader.onload = (function(_this) {
        return function() {
          if (file.type === "image/svg+xml") {
            if (callback != null) {
              callback();
            }
            return;
          }
          return createThumbnailFromUrl(file, fileReader.result, callback, width, height);
        };
        })(this);
        return fileReader.readAsDataURL(file);
    }
    function createThumbnailFromUrl(file, imageUrl, callback, crossOrigin, width, height) {
        var img;
        img = document.createElement("img");
        if (crossOrigin) {
            img.crossOrigin = crossOrigin;
        }
        img.onload = (function() {
            return function() {
                var canvas, ctx, resizeInfo, thumbnail, _ref, _ref1, _ref2, _ref3;
                file.width = img.width;
                file.height = img.height;
                resizeInfo = getResizeInfo(file, width, height);
                if (resizeInfo.trgWidth == null) {
                    resizeInfo.trgWidth = resizeInfo.optWidth;
                }
              if (resizeInfo.trgHeight == null) {
                resizeInfo.trgHeight = resizeInfo.optHeight;
              }
              canvas = document.createElement("canvas");
              ctx = canvas.getContext("2d");
              canvas.width = resizeInfo.trgWidth;
              canvas.height = resizeInfo.trgHeight;
              drawImageIOSFix(ctx, img, (_ref = resizeInfo.srcX) != null ? _ref : 0, (_ref1 = resizeInfo.srcY) != null ? _ref1 : 0, resizeInfo.srcWidth, resizeInfo.srcHeight, (_ref2 = resizeInfo.trgX) != null ? _ref2 : 0, (_ref3 = resizeInfo.trgY) != null ? _ref3 : 0, resizeInfo.trgWidth, resizeInfo.trgHeight);
              thumbnail = canvas.toDataURL("image/png");
              !!callback && callback(thumbnail);
            };
        })(this);

        if (callback != null) {
            img.onerror = callback;
        }

        return img.src = imageUrl;
    }
    
    function drawImageIOSFix (ctx, img, sx, sy, sw, sh, dx, dy, dw, dh) {
        var vertSquashRatio;
        vertSquashRatio = detectVerticalSquash(img);
        return ctx.drawImage(img, sx, sy, sw, sh, dx, dy, dw, dh / vertSquashRatio);
    }
    
    function detectVerticalSquash(img) {
        var alpha, canvas, ctx, data, ey, ih, iw, py, ratio, sy;
        iw = img.naturalWidth;
        ih = img.naturalHeight;
        canvas = document.createElement("canvas");
        canvas.width = 1;
        canvas.height = ih;
        ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        data = ctx.getImageData(0, 0, 1, ih).data;
        sy = 0;
        ey = ih;
        py = ih;
        while (py > sy) {
          alpha = data[(py - 1) * 4 + 3];
          if (alpha === 0) {
            ey = py;
          } else {
            sy = py;
          }
          py = (ey + sy) >> 1;
        }
        ratio = py / ih;
        if (ratio === 0) {
          return 1;
        } else {
          return ratio;
        }
    }
    
    function Uploader(element, options){
        this.element = element;
        this.options = options || this.defaultOptions();

        this.preview_wrapper = element.getElementsByClassName('upload-component-preview')[0];
        this.caption = element.getElementsByClassName('upload-component-caption')[0];
        this.input = element.getElementsByClassName('upload-component-input')[0];
        this.add_btn = element.getElementsByClassName('upload-component-add')[0];
        this.remove_btn = element.getElementsByClassName('upload-component-remove')[0];
        this.preview_caption = element.getElementsByClassName('upload-component-preview-caption')[0];

        this.input_name = this.input.getAttribute('name');

        this.initialContent = this.preview_wrapper.innerHTML;
        this._createInitialHtml();
        this.initialPreview = this.preview_wrapper.innerHTML;

        this._bindListeners();
    }

    Uploader.prototype.defaultOptions = function() {
        return {
            initialImagePath: false
        }
    };

    Uploader.prototype._createInitialHtml = function() {
        var _this = this;
        if(_this.options.initialImagePath)
        {
            _this.input.setAttribute('name', '');
            _this._addImagePreview(_this.options.initialImagePath);
        }
    };

    Uploader.prototype._addImagePreview = function(img_url) {
        var _this = this;
        _this.caption.classList.remove('hidden');

        function setPreview(img_url) {
            var image = document.createElement('img');
            image.setAttribute('class', 'upload-component-image');
            image.setAttribute('src', img_url);
            _this.preview_wrapper.innerHTML = '';
            _this.preview_wrapper.appendChild(image);
        }
        !!img_url ? setPreview(img_url) : createThumbnail(_this.input.files[0], setPreview, 500);
    };

    Uploader.prototype._removePreview = function() {
        var _this = this;

        _this.preview_wrapper.innerHTML = _this.options.initialImagePath ?
            _this.initialPreview : _this.initialContent;

        if(!_this.options.initialImagePath)
            _this.caption.classList.add('hidden');
    };

    Uploader.prototype._onInputChange = function(event) {
        var _this = this;
        if (_this.input.files && _this.input.files[0])
        {
            _this.hasFile = true;
            _this.input.setAttribute('name', _this.input_name);
            _this._addImagePreview();
        }
        else
        {
            _this.hasFile = false;
            _this._removePreview();
        }
    };

    Uploader.prototype.removeFile = function() {
        var _this = this;
        if(_this.options.initialImagePath && !_this.hasFile)
        {
            _this.options.initialImagePath = null;
            _this.input.value = '';
            _this.input.setAttribute('name', _this.input_name);
            _this._removePreview();
        }
        else if(_this.hasFile)
        {
            _this.input.value = '';
            _this.input.setAttribute('name', '');
            _this._onInputChange();
        }
    };

    Uploader.prototype._bindListeners = function() {
        var _this = this;
        _this.add_btn.addEventListener('click', function(event){
            event.preventDefault();
            _this.input.click()
        });

        _this.remove_btn.addEventListener('click', function(event){
            event.preventDefault();
            _this.removeFile();
        });

        _this.preview_wrapper.addEventListener('click', function(event){
            event.preventDefault();
            if (_this.input.files && _this.input.files[0]) {

            } else {
               _this.input.click();
            }
        });

        _this.input.addEventListener('change', _this._onInputChange.bind(_this));
    };

    return Uploader;
}));