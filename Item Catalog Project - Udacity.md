
# Item Catalog Project - Udacity

## Project Description

This is a  web page for a bookstore, where users can browse the store to see available books. Logged in users can add books and categories to the database.

## Features

* A databse made using Flask and SQLAlchemy  
* Fully functional CRUD operations
* Authentication process using Facebook and Google OAuth
* JSON Endpoints

### Initial Setup 

Running the project requires some software: 

* Install Vagrant 
* Install Virtual Box

### Starting vagrant 

* Using command line
* Browse to the extracted vagrant folder
* Type "vagrant up" and wait for initialization
* Type "vagrant ssh". Now you are logged in as vagrant
* Browse to "bookstore" folder
* run pip  install  -r  requirements.txt. This will install all the required dependencies.

### Running the database

First we must populate the database: 

* Run "python database_setup.py"
* Run "python books.py". This will add all the books and categories in the database
* Run "python server.py". This will initiate the server on localhost port 5000
* Go to http://localhost:5000 in browser to use the book database

### JSON Endpoints

* Visit "http://localhost:5000/bookstore/JSON" to get json data for all the books
* Visit "http://localhost:5000/bookstore/category/<int:category_id>/JSON" to retreive json data for individual books. <int:category_id> must be replaced with an integer. 

This README file was made using DILLINGER.
