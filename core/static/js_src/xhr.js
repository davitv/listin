(function(root){
    var aja = require('aja');
    var SINGLE_PRODUCT_URL = '/api/products/';

    var BRANCHES_URL = '/api/branches/';
    var ORGANIZATION_URL = '/api/organizations/my/';
    var CATEGORIES_URL = '/api/categories/';

    var noop = function(){};

    let get = (url, data, callback, fail) => aja()
                                        .method("GET")
                                        .url(url)
                                        .data(data)
                                        .on('success', callback)
                                        .on('fail', fail).go()

    module.exports = {
        product: function(id, callback, err) {
            err = err || noop;
            get(SINGLE_PRODUCT_URL + id + '/', {}, callback, err)
        },
        branches: function(organization_id, callback, err) {
            get(BRANCHES_URL, {organization_id}, callback, err)
        },
        organization: function(callback, err) {
            get(ORGANIZATION_URL, {}, callback, err)
        },
        categories: function(callback, err) {
            get(CATEGORIES_URL, {}, callback, err)
        }
    }



})(document);