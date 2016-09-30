import 'babel-polyfill'
import preinit from 'preinit'

import homepage from 'homepage'
import organization from 'organization'
import account from 'account'


preinit()

var routes = [
    ["^\/([a-z]{2}?\/)?$", 'homepage', homepage],
    ["^\/[a-z]{2}\/organization\/[a-z0-9A-Z_\/\-]*\/", 'organization', organization],
    ["^\/[a-z]{2}\/account\/$", 'account', account]
].map(([path, name, callback]) => {
    return {
        re: new RegExp(path),
        name: name,
        callback
    }
})

function mapRoute(pathname, routes) {
    routes.forEach(({re, callback}) => {
        if(pathname.match(re)){
            console.log(re, callback)
            callback()
        }
    })
}

function init(){
    let currentPath = window.location.pathname
    mapRoute(currentPath, routes)
}

init()
