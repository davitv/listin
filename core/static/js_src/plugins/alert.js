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
            ],
            function(  EvEmitter ) {
                return factory( window, EvEmitter);
            });
    } else if ( typeof exports == 'object' ) {
        // CommonJS
        module.exports = factory(
            window
        );
    } else {
        // browser global
        window.Alert = factory(
            window
        );
    }

}( window, function factory( window ) {

    'use strict';
// -------------------------- helpers -------------------------- //

    // extend objects
    function extend( a, b ) {
        for ( var prop in b ) {
            a[ prop ] = b[ prop ];
        }
        return a;
    }


    function Alert( element, options ) {
        this.element = element;
        this.option(options);
        this._create();
    }

    Alert.prototype.options = {
        className: "info",
        timeOut: 3000,
        text: "Hello! I am a default alert box!"
    };

    Alert.prototype.option = function( opts ) {
        extend( this.options, opts );
    };

    Alert.prototype._create = function() {
        var htmlNode = document.createElement("div");
        htmlNode.className = "alert alert-" + this.options.className;
        htmlNode.innerHTML = this.options.text;
        this.element.appendChild(htmlNode);
        setTimeout(function(){
            htmlNode.remove();
        }, this.options.timeOut)
    };




    return Alert;
}));