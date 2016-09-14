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
                'ev-emitter',
                'store'
            ],
            function(  EvEmitter, store ) {
                return factory( window, EvEmitter, store);
            });
    } else if ( typeof exports == 'object' ) {
        // CommonJS
        module.exports = factory(
            window,
            require('ev-emitter'),
            require('store')
        );
    } else {
        // browser global
        window.StoreWrapper = factory(
            window,
            window.EvEmitter,
            window.store
        );
    }

}( window, function factory( window, EvEmitter, store) {

    'use strict';
    function noop() {}


// -------------------------- helpers -------------------------- //

    // extend objects
    function extend( a, b ) {
        for ( var prop in b ) {
            a[ prop ] = b[ prop ];
        }
        return a;
    }

// --------------------------  -------------------------- //

    function StoreWrapper( options ) {

    }

    // inherit EvEmitter methods
    extend( StoreWrapper.prototype, EvEmitter.prototype );

    StoreWrapper.defaults = {

    };

    StoreWrapper.prototype.option = function( opts ) {
        extend( this.options, opts );
    };

    StoreWrapper.prototype.get = function( key ) {
        return store.get(key);
    };

    StoreWrapper.prototype.set = function( key, value ) {
        var res = store.set(key, value);
        this.emitEvent('itemAdded', key, value);
        return res;
    };



    return new StoreWrapper();
}));