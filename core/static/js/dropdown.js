/**
 * Created by davit on 2/15/16.
 */
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define([], factory);
    } else {
        // Browser globals
        root.Dropdown = factory(root.b);
    }
}(this, function () {
    var listener = null;
    var open = null;

    // http://stackoverflow.com/a/22119674
    function findAncestor (el, cls) {
        while ((el = el.parentElement) && !el.classList.contains(cls));
        return el;
    }

    function Dropdown(options){
        this._bindListeners();
    }

    Dropdown.prototype.toggle = function(event){

        var target = event.target;
        var el = (target.classList.contains('dropdown') ? target : findAncestor(target, 'dropdown'));
        if(el)
        {

            if(el.classList.contains('open'))
            {
                this.close();
            }
            else
            {
                event.preventDefault();
                this.close();
                el.classList.add('open');
                open = el;
            }
        } else {
            this.close();
        }
    };

    Dropdown.prototype._bindListeners = function() {
        if(listener) return;

        listener = this.toggle.bind(this);
        document.body.addEventListener('click', listener);
    };

    Dropdown.prototype._unBindListeners = function() {
        document.body.removeEventListener('click', listener);
    };

    Dropdown.prototype.close = function() {
       if(open)
       {
           open.classList.remove('open');
           open = null;
       }
    };

    return Dropdown;
}));