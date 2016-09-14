
var path = require('path');
var webpack = require('webpack');
var JS_ROOT = (__dirname + '/js_src/');

module.exports = {
  entry: './js_src/app.js',
  output: { path: __dirname, filename: './js_dist/app.js' },
  module: {
    loaders: [
      {
        test: /.js?$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        query: {
          presets: ['es2015', 'react']
        }
      }
    ]
  },
  resolve: {
    root: [
      path.resolve(JS_ROOT)
    ]
  }

};