var express = require('express')
var app = express()
var ObjectId = require('mongodb').ObjectId
var evalidator  = require("express-validator")
var moment = require('moment')
// list of user
app.get('/', function(req, res, next) {	
	// fetch and sort user  by id in descending order
	req.db.collection('crud').find().sort({"_id": -1}).toArray(function(err, result) {
		//if (err) return console.log(err)
		if (err) {
			req.flash('error', err)
			res.render('user/list', {
				title: 'User List', 
				data: ''
			})
		} else {
			// render to views/user/list.ejs template file
			res.render('user/list', {
				title: 'User List', 
				data: result
			})
		}
	})
})

// SHOW ADD USER FORM
app.get('/add', function(req, res, next){	
	// render to views/user/add.ejs
	res.render('user/add', {
		title: 'Add New User',
		name: '',
		gender: '',
		email: '',
		dob : '',
		phone: '',
		cur_org: '',
		zip: '',
		state: '',
		city: '',
		country: ''
	})
})

// ADD NEW USER POST ACTION
app.post('/add', function(req, res, next){	
	req.assert('name', 'Name is required').notEmpty()           //Validate name
	req.assert('gender', 'Gender is required').notEmpty()       //Validate Gender
    req.assert('email', 'A valid email is required').isEmail()  //Validate email
	req.assert('dob', 'Please enter valid date').isDate()
	req.assert('phone','Phone Number is required').notEmpty()
	req.assert('phone','Please enter valid Mobile Number').isInt().isLength({min: 10})
	req.assert('cur_org', 'Organisation Name is required').notEmpty()           //Validate name
        req.assert('zip', 'Zip code is required').notEmpty() 
	req.assert('zip', 'Please enter valid pin code').isInt().isLength({min: 6, max: 6})
	req.assert('state','State is required').notEmpty()
	req.assert('city', 'City is required').notEmpty()
        req.assert('country','Country is required').notEmpty()


    var errors = req.validationErrors()  //warnings
    
    if( !errors ) {   //No errors were found.  Passed Validation!
		
		var user = {
			name: req.sanitize('name').escape().trim(),
			gender: req.sanitize('gender').escape().trim(),
			email: req.sanitize('email').escape().trim(),
			dob: req.sanitize('dob').escape().trim(),
			phone: req.sanitize('phone').escape().trim(),
			cur_org: req.sanitize('cur_org').escape().trim(),
                        zip: req.sanitize('zip').escape().trim(),
                        state: req.sanitize('state').escape().trim(),
                        city: req.sanitize('city').escape().trim(),
			country: req.sanitize('country').escape().trim()
		}
				 
		req.db.collection('crud').insert(user, function(err, result) {
			if (err) {
				req.flash('error', err)
				
				// render to views/user/add.ejs
				res.render('user/add', {
					title: 'Add New User',
					name: user.name,
					gender: user.gender,
					email: user.email,
					dob: user.dob,
					phone: user.phone,
					cur_org: user.cur_org,
					zip: user.zip,
					state: user.state,
					city: user.city,
					country: user.country
				})
			} else {				
				req.flash('success', 'Data added successfully!')
				
				// redirect to user list page				
				res.redirect('/users')
				
			
			}
		})		
	}
	else {   //Display errors to user
		var error_msg = ''
		errors.forEach(function(error) {
			error_msg += error.msg + '<br>'
		})				
		req.flash('error', error_msg)		
		
		/**
		 * Using req.body.name 
		 * because req.param('name') is deprecated //err fix
		 */ 
        res.render('user/add', { 
            title: 'Add New User',
            name: req.body.name,
            gender: req.body.gender,
            email: req.body.email,
	    dob: req.body.dob,
            phone: req.body.phone,
	    cur_org: req.body.cur_org,
	    zip: req.body.zip,
            state: req.body.state,
            city: req.body.city,
            country: req.body.country
       })
    }
})

// SHOW EDIT USER FORM
app.get('/edit/(:id)', function(req, res, next){
	var o_id = new ObjectId(req.params.id)
	req.db.collection('crud').find({"_id": o_id}).toArray(function(err, result) {
		if(err) return console.log(err)
		
		// if user not found
		if (!result) {
			req.flash('error', 'User not found with id = ' + req.params.id)
			res.redirect('/users')
		}
		else { // if user found
			// render to views/user/edit.ejs template file
			res.render('user/edit', {
				title: 'Edit User', 
				//data: rows[0],
				id: result[0]._id,
				name: result[0].name,
			
				email: result[0].email,
				dob: result[0].dob,
				phone: result[0].phone,
				cur_org: result[0].cur_org,
				zip: result[0].zip,
            state: result[0].state,
            city: result[0].city,
            country: result[0].country
			})
		}
	})	
})
// EDIT USER POST ACTION
app.put('/edit/(:id)', function(req, res, next) {
	req.assert('name', 'Name is required').notEmpty()           //Validate name
	
    req.assert('email', 'A valid email is required').isEmail()  //Validate email
	req.assert('phone','Phone Number is required').notEmpty()
	req.assert('phone','Please enter valid Mobile Number').isInt().isLength({min: 10})
        req.assert('cur_org', 'Organisation Name is required').notEmpty()           //Validate name
        req.assert('zip', 'Zip code is required').notEmpty()
	req.assert('zip', 'Enter valid pin code').isInt().isLength({min: 6, max: 6})
        req.assert('state','State is required').notEmpty()
        req.assert('city', 'City is required').notEmpty()
        req.assert('country','Country is required').notEmpty()

    var errors = req.validationErrors()  //req.getValidationResult()// fixed
    
    if( !errors ) {   //No errors were found.  Passed Validation!
		
		var user = {
			name: req.sanitize('name').escape().trim(),
			
			email: req.sanitize('email').escape().trim(),
			phone: req.sanitize('phone').escape().trim(),
                        cur_org: req.sanitize('cur_org').escape().trim(),
                        zip: req.sanitize('zip').escape().trim(),
                        state: req.sanitize('state').escape().trim(),
                        city: req.sanitize('city').escape().trim(),
                        country: req.sanitize('country').escape().trim()
			
		}
		
		var o_id = new ObjectId(req.params.id)
		req.db.collection('crud').update({"_id": o_id},{$set: user}, function(err, result) {
			if (err) {
				req.flash('error', err)
				
				// render to views/user/edit.ejs
				res.render('user/edit', {
					title: 'Edit User',
					id: req.params.id,
					name: req.body.name,
					
					email: req.body.email,

            phone: req.body.phone,
            cur_org: req.body.cur_org,
            zip: req.body.zip,
            state: req.body.state,
            city: req.body.city,
            country: req.body.country

				})
			} else {
				req.flash('success', 'Done successfully!')
				
				res.redirect('/users')
				
			
			}
		})		
	}
	else {   //Display errors to user
		var error_msg = ''
		errors.forEach(function(error) {
			error_msg += error.msg + '<br>'
		})
		req.flash('error', error_msg)
		
		/**
		 * Using req.body.name 
		 * because req.param('name') is deprecated - err fixed
		 */ 
        res.render('user/edit', { 
            title: 'Edit User',            
			id: req.params.id, 
			name: req.body.name,
			
			email: req.body.email,
			phone: req.body.phone,
            cur_org: req.body.cur_org,
            zip: req.body.zip,
            state: req.body.state,
            city: req.body.city,
            country: req.body.country

        })
    }
})

// DELETE USER
app.delete('/delete/(:id)', function(req, res, next) {	
	var o_id = new ObjectId(req.params.id)
	req.db.collection('crud').remove({"_id": o_id}, function(err, result) {
		if (err) {
			req.flash('error', err)
			// redirect to users list page
			res.redirect('/users')
		} else {
			req.flash('success', 'User deleted successfully!')
			// redirect to users list page
			res.redirect('/users')
		}
	})	
})

module.exports = app
