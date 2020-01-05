var express = require('express')
var app = express()
//var path = require('path')

//app.use('/static', express.static('views'))

//app.use('/static', express.static(path.join(__dirname, 'views')))

//var views = require('./views')
app.use(express.static('views'))


app.listen(3000, function(){
	console.log('Server running at port 3000 on localhost : http://192.168.0.104:3000')
})
