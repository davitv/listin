(function(root){
    var aja = require('aja');
    var SINGLE_PRODUCT_URL = '/api/products/';
    var noop = function(){};

    module.exports = {
        product: function(id, callback, err) {
            err = err || noop;
            aja().url(SINGLE_PRODUCT_URL + id + '/').method('GET')
                .on('success', callback).on('fail', err).go();
        }
    }



})(document);