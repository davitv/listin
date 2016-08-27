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
        window.Tabs = factory(
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

    function Tabs( element, options ) {
        this.element = element;
        // options
        this.options = extend( {}, this.constructor.defaults );
        this.option( options );
        this.togglers =  element.getElementsByClassName('toggler');
        this.content  =  element.getElementsByClassName('tab-content');
        this.current  = -1;
        this._create();
    }

    // inherit EventEmitter methods
    //extend( Sidebar.prototype, EventEmitter.prototype );

    Tabs.defaults = {
        // content fetching url
        url: false
    };

    /**
     * set options
     * @param {Object} opts
     */
    Tabs.prototype.option = function( opts ) {
        extend( this.options, opts );
    };

    Tabs.prototype._create = function() {

        var _this = this;

        for(var i = 0, l = this.togglers.length; i < l; i++)
        {
            if(hasClass(this.togglers[i], 'active'))
            {
                this.current = i;
            }
            (function(index, toggler){
                toggler.addEventListener('click', function(event){
                    event.preventDefault();
                    if(_this.current != -1)
                    {
                        removeClass(_this.content[_this.current], 'active');
                        removeClass(_this.togglers[_this.current], 'active');

                    }
                    addClass(_this.content[index], 'active');
                    addClass(_this.togglers[index], 'active');
                    _this.current = index;
                });
            })(i, this.togglers[i]);
        }
    };

    Tabs.prototype.toggleNode = function(elem){
        var open = hasClass(elem, 'open') ? 1 : 0;
        if(open)
        {
            removeClass(elem, 'open');
            removeClass(elem.getElementsByClassName('open'), 'open');
        } else {
            addClass(elem, 'open');
        }
    };

    Tabs.prototype.getActiveToggler = function(){
        return this.togglers[this.current];
    };

    return Tabs;
}));