/*!
 * Simodal v0.1.0 - https://github.com/davitv/simodal
 * Unlicense - http://unlicense.org/
 * Vardanyan Davit - https://github.com/davitv
 * @preserve
 */
( function( window, factory ) {
    'use strict';

    if ( typeof define == 'function' && define.amd ) {
        // AMD
        define( [
                'eventEmitter/EventEmitter'
            ],
            function( classie, EventEmitter ) {
                return factory( window, EventEmitter);
            });
    } else if ( typeof exports == 'object' ) {
        // CommonJS
        module.exports = factory(
            window,
            require('eventEmitter/EventEmitter')
        );
    } else {
        // browser global
        window.Simodal = factory(
            window,
            window.EventEmitter
        );
    }

}( window, function factory( window, EventEmitter) {

    'use strict';

    // vars
    var document = window.document;

    function noop() {}


// -------------------------- helpers -------------------------- //

    // extend objects
    function extend( a, b ) {
        for ( var prop in b ) {
            a[ prop ] = b[ prop ];
        }
        return a;
    }

    // http://stackoverflow.com/a/384380/182183
    var isElement = ( typeof HTMLElement == 'object' ) ?
        function isElementDOM2( obj ) {
            return obj instanceof HTMLElement;
        } :
        function isElementQuirky( obj ) {
            return obj && typeof obj == 'object' &&
                obj.nodeType == 1 && typeof obj.nodeName == 'string';
        };

    /**
     * IE 5.5+, Firefox, Opera, Chrome, Safari XHR object
     * https://gist.github.com/Xeoncross/7663273#file-ajax-js
     *
     * @param url string
     * @param callback object
     * @param data mixed
     * @param x null
     */
    function ajax(url, callback, data, x) {
        try {
            x = new(window.XMLHttpRequest || ActiveXObject)('MSXML2.XMLHTTP.3.0');
            x.open(data ? 'POST' : 'GET', url, 1);
            x.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            x.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
            x.onreadystatechange = function () {
                x.readyState > 3 && callback && callback(x.responseText, x);
            };
            x.send(data)
        } catch (e) {
            window.console && console.log(e);
        }
    }

    // http://jaketrent.com/post/addremove-classes-raw-javascript/
    function hasClass(el, className) {
        if (el.classList)
            return el.classList.contains(className);
        else
            return !!el.className.match(new RegExp('(\\s|^)' + className + '(\\s|$)'));
    }

    function addClass(el, className) {
        if (el.classList)
            el.classList.add(className);
        else if (!hasClass(el, className)) el.className += " " + className
    }

    function removeClass(el, className) {
        if (el.classList)
            el.classList.remove(className);
        else if (hasClass(el, className)) {
            var reg = new RegExp('(\\s|^)' + className + '(\\s|$)');
            el.className=el.className.replace(reg, ' ')
        }
    }

    // http://stackoverflow.com/a/13382873
    function getScrollbarWidth() {
        var outer = document.createElement("div");
        outer.style.visibility = "hidden";
        outer.style.width = "100px";
        outer.style.msOverflowStyle = "scrollbar"; // needed for WinJS apps

        document.body.appendChild(outer);

        var widthNoScroll = outer.offsetWidth;
        // force scrollbars
        outer.style.overflow = "scroll";

        // add innerdiv
        var inner = document.createElement("div");
        inner.style.width = "100%";
        outer.appendChild(inner);

        var widthWithScroll = inner.offsetWidth;

        // remove divs
        outer.parentNode.removeChild(outer);

        return widthNoScroll - widthWithScroll;
    }

// --------------------------  -------------------------- //

    function Simodal( options ) {

        // options
        this.options = extend( {}, this.constructor.defaults );
        this.option( options );

        this._create();
    }
    Simodal.overlays = {};

    // inherit EventEmitter methods
    extend( Simodal.prototype, EventEmitter.prototype );

    Simodal.defaults = {

        // content fetching url
        url: false,

        // modal window content, can be plain HTML string or DOM node
        // if url option was specified, this will be shown during loading
        content: false,

        // immediately show after instantiating
        show: true,

        // pressing "escape" will close the window
        keyboard: true,

        // default class for modal window
        modalClass: 'simodal',

        // default class for overlay
        overlayClass: 'simodal-overlay',

        // element class which will be a trigger for hiding
        closersClass: 'simodal-close',

        // "submit" event triggering
        submitClass: 'simodal-submit',

        // "cancel" event triggering
        cancelClass: 'simodal-cancel',

        // adding after modal is shown
        modalOnShowClass: '',

        // adding before modal is hidden
        modalOnHideClass: '',

        // added for showing modal
        overlayOnShowClass: 'open',

        // added before hiding modal
        overlayOnHideClass: '',

        // overlay click will close modal
        overlayClick: true,

        // remove modal HTML node after hiding it
        removeOnHide: false,

        // should modal be closed when clicking on it
        closeOnClick: false,

        // "modal" or "notification"
        kind: 'modal'
    };

    /**
     * set options
     * @param {Object} opts
     */
    Simodal.prototype.option = function( opts ) {
        extend( this.options, opts );
    };

    Simodal.prototype._insertHTML = function(elem, content){
        if(isElement(content))
            elem.appendChild(content);
        else
            elem.innerHTML = content;
    };

    Simodal.prototype._create = function() {

        // constructing html
        this.overlay = this._getOverlay();
        this.modal = this._getModalWindow();
        this.overlay.appendChild(this.modal);
        if(this.options.url)
        {
            var _this = this;

            if(this.options.content)
            {
                this._insertHTML(this.modal, this.options.content);
                this._onInit();
            }

            ajax(this.options.url, function(res){
                _this.modal.innerHTML = res;
                if(!_this.options.content)
                {
                    _this._onInit();
                }
                _this.emit('ajaxLoaded');
            });
        }
        else if(this.options.content)
        {
            this._insertHTML(this.modal, this.options.content);
            this._onInit();
        }
    };

    // constructing HTML ---------------------------------/
    Simodal.prototype._getOverlay = function() {

        // do not create new overlay with same class if there is already exists one
        if (this.options.kind == 'notification' && !!Simodal.overlays[this.options.overlayClass])
        {
            return Simodal.overlays[this.options.overlayClass];
        }


        var overlay = document.createElement('div');
        this.addClass(overlay, this.options.overlayClass);

        // without tabindex escape button event will not trigger
        overlay.tabIndex = "-1";

        if(this.options.kind == 'notification')  Simodal.overlays[this.options.overlayClass] = overlay;
        document.body.appendChild(overlay);
        return overlay;
    };

    Simodal.prototype._getModalWindow = function() {
        var modal = document.createElement('div');
        this.addClass(modal, this.options.modalClass);
        return modal;
    };

    Simodal.prototype.addClass = function(elem, cls) {
        var clss = cls.trim().split(' ');
        for(var i = 0, l = clss.length; i<l; i++)
        {
            addClass(elem, clss[i]);
        }
    };

    Simodal.prototype._onInit = function() {
        this._initEventListeners();

        if(this.options.show)
        {
            this.show();
        }
    };

    Simodal.prototype._initEventListeners = function() {

        var closers = this.modal.getElementsByClassName(this.options.closersClass),
            _this = this;
        for(var i = 0, l = closers.length; i < l; i++)
        {
            closers[i].addEventListener('click', function(event){
                event.preventDefault();
                _this.hide();
            });
        }

        // clicking on modal will close it (useful for notifications)
        if(this.options.closeOnClick){
            this.modal.addEventListener('click', function(event){
                event.preventDefault();
                _this.hide();
            });
        }

        var submit_btns = this.overlay.getElementsByClassName(this.options.submitClass);
        for(i = 0, l = submit_btns.length; i < l; i++)
        {
            submit_btns[i].addEventListener('click', function(event){
                event.preventDefault();
                _this.onSubmit(this);
            });
        }

        var cancel_btns = this.overlay.getElementsByClassName(this.options.cancelClass);
        for(i = 0, l = submit_btns.length; i < l; i++)
        {
            cancel_btns[i].addEventListener('click', function(event){
                event.preventDefault();
                _this.onCancel(this);
            });
        }

        if(this.options.kind == 'modal')
        {
            if(this.options.keyboard){
                this.overlay.addEventListener('keydown', function(event){
                    if(event.which == 27)
                    {
                        _this.hide();
                    }
                });
            }

            if(this.options.overlayClick){
                this.overlay.addEventListener('click', function(event){
                    _this.hide();
                });

                // prevent modal click bubbling to overlay
                this.modal.addEventListener('click', function(event){
                    event.stopPropagation();
                    event.stopImmediatePropagation();
                });
            }
        }
    };

    Simodal.prototype.show = function() {
        if(this.options.kind == 'modal')
        {
            var scrollBarWidth = getScrollbarWidth();
            document.body.style['overflow'] = 'hidden';
            document.body.style['padding-right'] = scrollBarWidth + 'px';
        }

        addClass(this.overlay, this.options.overlayOnShowClass);
        if(this.options.modalOnShowClass)
            this.addClass(this.modal, this.options.modalOnShowClass);

        if(this.options.keyboard)
        {
            // focusing for being able to trigger keypress event
            this.overlay.focus();
        }

        this.emit('show');
    };

    Simodal.prototype.hide = function() {
        var _this = this;

        function hideModal(){
            if(_this.options.kind == 'modal')
            {
                document.body.style['overflow'] = 'auto';
                document.body.style['padding-right'] = '0';
                if(_this.options.removeOnHide)
                {
                    _this.overlay.remove();
                }
                else
                {
                    removeClass(_this.overlay, _this.options.overlayOnShowClass);
                }

            }
            else if(_this.options.kind == 'notification')
            {
                _this.modal.remove();
                var notes = _this.overlay.getElementsByClassName(_this.options.modalClass);
                if(!notes.length)
                {
                    _this.overlay.remove();
                    Simodal.overlays[_this.options.overlayClass] = null;
                }
            }
            _this.emit('hide');
        }

        if(this.options.modalOnHideClass)
        {
            // TODO: add event listener for animation end
            this.addClass(this.modal, this.options.modalOnHideClass);
        }
        else
        {
            hideModal();
        }
    };

    Simodal.prototype.onSubmit = function(clicked_elem) {
        this.emit('submit', clicked_elem)
    };

    Simodal.prototype.onCancel = function(clicked_elem) {
        this.emit('cancel', clicked_elem)
    };

    return Simodal;
}));