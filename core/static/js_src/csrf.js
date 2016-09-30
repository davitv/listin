import cookies from 'js-cookie'

var csrf_token = cookies.get('csrftoken')

module.exports = csrf_token