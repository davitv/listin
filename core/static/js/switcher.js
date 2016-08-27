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
        window.Switcher = factory(
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
    function closest(el, selector) {
        var matchesFn;

        // find vendor prefix
        ['matches','webkitMatchesSelector','mozMatchesSelector','msMatchesSelector','oMatchesSelector'].some(function(fn) {
            if (typeof document.body[fn] == 'function') {
                matchesFn = fn;
                return true;
            }
            return false;
        });

        if(el[matchesFn](selector)) return el;

        // traverse parents
        while (el!==null) {
            var parent = el.parentElement;
            if (parent!==null && parent[matchesFn](selector)) {
                return parent;
            }
            el = parent;
        }

        return null;
    }

    // http://jaketrent.com/post/addremove-classes-raw-javascript/
    function hasClass(el, className) {

        if (el.classList)
            return el.classList.contains(className);
        else
            return !!el.className.match(new RegExp('(\\s|^)' + className + '(\\s|$)'));
    }

    function addClass(el, className) {
        var elems = isElement(el) ? [el] : el;
        for(var i = elems.length - 1; i >= 0; i--)
        {
            if (elems[i].classList)
                elems[i].classList.add(className);
            else if (!hasClass(elems[i], className)) elems[i].className += " " + className
        }

    }

    function removeClass(el, className) {
        var elems = isElement(el) ? [el] : el;
        for(var i = elems.length - 1; i >= 0; i--)
        {
            if (elems[i].classList)
                elems[i].classList.remove(className);
            else if (hasClass(elems[i], className)) {
                var reg = new RegExp('(\\s|^)' + className + '(\\s|$)');
                elems[i].className=elems[i].className.replace(reg, ' ')
            }
        }
    }


// --------------------------  -------------------------- //

    function Switcher( togglersWrapper, togglingContent, options ) {

        // options
        this.options = extend( {}, this.constructor.defaults );
        this.option( options );
        this.togglersWrapper = togglersWrapper;
        this.togglingContent = togglingContent;
        this.togglers = togglersWrapper.getElementsByClassName('toggler');
        this.tabContents =  togglingContent.getElementsByClassName(this.options.contentClass);
        this.current = -1;
        for(var i = 0, l = this.tabContents.length; i < l; i++)
        {
            if(hasClass(this.tabContents[i], 'open'))
            {
                this.current = i;
                break;
            }
        }
        this._bindListeners();
    }

    // inherit EventEmitter methods
    //extend( Switcher.prototype, EventEmitter.prototype );

    Switcher.defaults = {
        togglerSelector: ".toggler",
        contentClass: "tab-content"
    };

    /**
     * set options
     * @param {Object} opts
     */
    Switcher.prototype.option = function( opts ) {
        extend( this.options, opts );
    };

    Switcher.prototype._bindListeners = function(  ) {
        var _this = this;
        this.togglersWrapper.addEventListener('click', function(event){
            var switcher = closest(event.target, _this.options.togglerSelector);
            if(switcher)
            {
                event.preventDefault();
                _this.toggle(switcher);
            }
        });
    };


    Switcher.prototype.toggle = function( switcher ) {
        var index = Array.prototype.indexOf.call(switcher.parentNode.children, switcher);
        if(this.current != index && index != -1)
        {
            removeClass(this.tabContents[this.current], 'open')
            removeClass(this.togglers[this.current], 'active')
        }
        addClass(this.tabContents[index], 'open');
        addClass(switcher, 'active');
        this.current = index;
    };


    return Switcher;
}));