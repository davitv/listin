(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define([], function () {
            // Also create a global in case some scripts
            // that are loaded still are looking for
            // a global even when an AMD loader is in use.
            return factory();
        });
    } else {
        // Browser globals
        root.dom = factory();
    }
}(this, function () {

    function dom(){

    }

    dom.prototype.select = function(selector, context){
        return (context || document).querySelectorAll(selector);
    };

    dom.prototype.select1 = function(selector, context){
        return (context || document).querySelector(selector);
    };

    dom.prototype.create = function(tagname, classes, id){
        var elem = document.createElement(tagname);
        if(classes) elem.className = classes;
        if(id) elem.id = id;
        return elem;
    };

    dom.prototype.size = function(elem){
        return [elem.offsetWidth, elem.offsetHeight];
    };
    dom.prototype.closest = function(el, selector) {
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
            parent = el.parentElement;
            if (parent!==null && parent[matchesFn](selector)) {
                return parent;
            }
            el = parent;
        }

        return null;
    };

    return new dom();
}));