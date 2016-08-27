/**
 * cart.js
 *
 * Licensed under the MIT license.
 * http://www.opensource.org/licenses/mit-license.php
 *
 * Copyright 2016, Listin
 * http://www.listin.ru
 */
(function (window) {
    'use strict';

    var store = require('store');
    var DEFAULT_STORAGE_KEY = 'cartjs';
    var INITIAL_STORAGE_OBJECT = {
        items: [],
        totals: {
            price: 0,
            amount: 0
        }
    };

    function Cart(storage_key){
        this.storage_key = storage_key || DEFAULT_STORAGE_KEY;
    }

    Cart.prototype.add = function(item, amount){

        amount = (!!amount ? amount : 1);
        var items = this.getState().items;
        var added_item = false;
        
        for(var i = 0, l = items.length; i < l; i++)
        {
            if(item.id === items[i].id)
            {
                added_item = items[i];
                break;
            }
        }
        if(!added_item)
        {
            added_item = item;
            added_item['amount'] = amount;
            added_item['total_price'] = parseFloat(amount * item.price);
            items.push(added_item)
        }
        else
        {
            added_item['amount'] += amount;
            added_item['total_price'] = parseFloat(amount * item.price);
        }
    };

    Cart.prototype.remove = function(product){

    };

    Cart.prototype.totalAmount = function(product){

    };

    Cart.prototype.getProduct = function(item_id){
        var items = this.getState().items;
        for(var i = 0, l = items.length; i < l; i++)
        {
            if(item_id === items[i].id) return items[i];
        }
        return null;
    };

    Cart.prototype.getState = function(){
        var cached = store.get(this.storage_key);
        return (cached ? JSON.parse(cached) : INITIAL_STORAGE_OBJECT);
    };

    Cart.prototype.setState = function(state){
        store.set(this.storage_key, JSON.stringify(state));
    };


    return Cart;
})(window);

