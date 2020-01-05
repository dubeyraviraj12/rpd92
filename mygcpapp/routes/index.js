var express = require('express')
var app = express()

app.get('/', function(req, res) {
	// render to views/index.ejs template file
	res.render('index', {title: 'Home Page of CRUD'}) //it become title in browser tab
})

/** 
  * module.exports exposes the app object as a module
 * module.exports  used to return the object when this file is required in another module like app.js
 */ 
module.exports = app;
