from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Book, User
from flask import session as login_session
import random
import string
from flask import Flask, render_template
from flask import request, redirect, url_for, jsonify, flash
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json

from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "bookstore"

app = Flask(__name__)

engine = create_engine('sqlite:///bookstore.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# ==============================================
# This OAuth button for Google and Facebook code is mostly
# from instructors lessons and code provided in the project
# =========================================================


# Token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)
# Facebook Login


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret'
           '=%s&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')
    url = ('https://graph.facebook.com/v2.8/me?access_token'
           '=%s&fields=name,id,email') % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['access_token'] = token

    # user picture
    url = ('https://graph.facebook.com/v2.8/me/'
           'picture?access_token=%s&redirect=0&height=200&width=200') % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # access token for loggin out
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/%s/'
           'permissions?access_token=%s') % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# This does not work yet. Please ignore. gconnect method


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.header['content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps
                                 ('Failed to upgrade the authorization code.'),
                                 401)
        response.headers['content-type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 50)
        response.headers['content-Type'] = 'application/json'

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps
                                 ("Token user doesnt mathch the given id"),
                                 401)
        response.headers['Content-type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token id does not match"), 401)
        print "Token id does not match the app's"
        response.headers['content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# JSON APIs to view Book database information


@app.route('/bookstore/JSON')
def booksJSON():
    items = session.query(Book).all()
    return jsonify(Category=[i.serialize for i in items])


@app.route('/bookstore/category/<int:category_id>/JSON')
def showBookbyCategoryJSON(category_id):
    categories = session.query(Category).filter_by(id=category_id).first()
    books = session.query(Book).filter_by(category_id=category_id).all()
    return jsonify(Book=[i.serialize for i in books])

# Main page/shows all the available categories


@app.route('/')
@app.route('/bookstore/')
def showcategories():
    categories = session.query(Category).all()
    items = session.query(Book).order_by(Book.id.desc())
    return render_template('main.html', categories=categories, items=items)

# Show all books


@app.route('/bookstore/books/')
def showAllBooks():
    books = session.query(Book).all()
# delete this
    user = session.query(User).all()
    return render_template('allBooks.html', books=books, user=user)

# show books by category


@app.route('/bookstore/catalog/<int:category_id>/category')
def showBooks(category_id):
    categories = session.query(Category).filter_by(id=category_id).first()
    books = session.query(Book).filter_by(category_id=category_id).all()
    return render_template('category.html', categories=categories, books=books)

# show description of each book in a category


@app.route('/bookstore/catalog/<int:book_id>/bookdetails')
def bookDetails(book_id):
    item = session.query(Book).filter_by(id=book_id).one()
    return render_template('bookDetails.html', item=item)

# Add delete button


@app.route('/bookstore/catalog/<int:book_id>/delete', methods=['GET', 'POST'])
def deleteBook(book_id):
    if 'username' not in login_session:
        return redirect('/login')
# Ensuring only the user who has added a book is authorized to delete it
    item = session.query(Book).filter_by(id=book_id).one()
    creator = getUserInfo(item.user_id)
    if item.user_id != login_session['user_id']:
        return ("<script>function myFunction() "
                "{alert('You are not authorized to delete this item.\
                Go Back to Homepage to create your own item.');}\
                </script><body onload='myFunction()'>")
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('showcategories'))
    else:
        return render_template('deleteBook.html', item=book_id)

# Add edit button


@app.route('/bookstore/catalog/<int:book_id>/edit', methods=['GET', 'POST'])
def editBook(book_id):
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Book).filter_by(id=book_id).one()
    # Ensuring only the user who has added a book is authorized to delete it
    creator = getUserInfo(item.user_id)
    if item.user_id != login_session['user_id']:
        return ("<script>function myFunction() "
                "{alert('You are not authorized to edit this item.\
                Go Back to Homepage to create your own item.');}\
                </script><body onload='myFunction()'>")

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
            return redirect(url_for('showcategories'))
    else:
        return render_template('editBook.html', item=book_id)

# Add a new book


@app.route('/bookstore/newbook', methods=['GET', 'POST'])
def addBook():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newBook = Book(category_id=request.form['category'],
                       user_id=login_session['user_id'],
                       name=request.form['name'],
                       description=request.form['description'])
        session.add(newBook)
        session.commit()
        flash("New book added")
        return redirect(url_for('showcategories'))
    else:
        return render_template('newBook.html')


@app.route('/bookstore/newcategory', methods=['GET', 'POST'])
def addCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        flash("New Category Added")
        return redirect(url_for('showcategories'))
    else:
        return render_template('newCategory.html')

# Disconnect


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have been logged out.")
        return redirect(url_for('showcategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showcategories'))


if __name__ == '__main__':
    app.secret_key = 'supersecretkey'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
