import organization from 'organization'


var routes = [
    ["/[a-z]{2}/organization/[a-z0-9A-Z_\/\-]*/", 'organization', organization]
].map(([path, name, callback]) => {
    return {
        re: new RegExp(path),
        name: name,
        callback
    }
})

function mapRoute(pathname, routes) {
    routes.forEach(({re, callback}) => {
        if(pathname.match(re))
            callback()
    })
}

function init(){
    let currentPath = window.location.pathname
    mapRoute(currentPath, routes)
}

init()
