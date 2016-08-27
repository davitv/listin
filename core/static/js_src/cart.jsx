(function(document){
  'use strict';

  // vendor
  var EventEmitter = require('event-emitter');
  // ========================================== //

  var CartComponent = require('./jsx/cart.jsx')
  var transport = require('./transport');

  var emitter = EventEmitter({});

  var MARKET_CART_WRAPPER_ID = 'market-cart';
  var MARKET_ADD_TO_CART_CLASS = 'js-add-to-cart';

  ReactDOM.render(<CartComponent transport={transport} emitter={emitter} />, document.getElementById(MARKET_CART_WRAPPER_ID));
  
  var cartButtons = document.getElementsByClassName(MARKET_ADD_TO_CART_CLASS);

  for (var i = 0, l = cartButtons.length; i < l; i++) {
    cartButtons[i].addEventListener('click', function(event){
        event.preventDefault();
        emitter.emit('product-added', this.href.slice(-1));
    });  
  }

})(window.document);
