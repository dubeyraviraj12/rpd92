var express = require('express')
var app = express()
var chalk = require("chalk")
var connected = chalk.bold.cyan;
var dbok = chalk.bold.green;
var path = require("path")

var expressMongoDb = require('express-mongo-db');
/**
 * Load database credentials  config.js file
 */ 
var config = require('./config')
app.use(expressMongoDb(config.database.url));
console.log(dbok('DB Connected'));

/**
 * setting up the templating view engine
 */ 
app.set('view engine', 'ejs')

/**
 * import routes
  */ 
var index = require('./routes/index')
var users = require('./routes/users')

/**
 * Express Validator Middleware for Form Validation
 */ 
var expressValidator = require('express-validator')
app.use(expressValidator())

/**
 * body-parser module is used to read HTTP POST data
 */ 
var bodyParser = require('body-parser')
/**
 * bodyParser.urlencoded() parses the text as URL encoded data 
 */ 
app.use(bodyParser.urlencoded({ extended: true }))
app.use(bodyParser.json())


/**
 * This module let us use HTTP verbs such as PUT or DELETE 
 * in places where they are not supported
 */ 
 var methodOverride = require('method-override')

app.use(methodOverride(function (req, res) {
  if (req.body && typeof req.body === 'object' && '_method' in req.body) {
  // look in urlencoded POST bodies and delete it
  var method = req.body._method
    delete req.body._method
    return method
  }
}))


/**
 * This module shows flash messages
  * Flash messages are stored in session
 * So, we use cookie-parser & session modules
 */ 
var flash = require('express-flash')

//We may skip cookie-parser Since version 1.5.0, the cookie-parser middleware 
//no longer needs to be used for this module to work
//var cookieParser = require('cookie-parser');
var session = require('express-session');

//app.use(cookieParser('tcs alpha'))
app.use(session({ 
	secret: 'tcs alpha',
	resave: false,
	saveUninitialized: true,
	cookie: { maxAge: 60000 } //60000ms
}))

app.use(flash())
// img
app.use(express.static(path.join(__dirname + '/views')));
//routers
app.use('/', index)
app.use('/users', users)



app.listen(3030, function(){
	console.log(connected('Server running at port 3030 -  http://3.16.136.60:3030 '))
})
