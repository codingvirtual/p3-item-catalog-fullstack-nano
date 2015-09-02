# Category:
#   List, Add, Edit, Delete, JSON endpoint
#   QUESTIONS: If deleting a category, what to do with items from the category?
#       Reassign
#       Delete the items as well

# Items in a category:
#   List, Add, Edit, Delete, JSON endpoint

from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

linkVisibility = 'hide'
buttonVisibility = 'show'
messages = []
CLIENT_ID = json.loads(
    open('../client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///supporting-files/catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    #return "The current session state is %s" %login_session['state']
    return render_template('sign_in.html', state=state)

# OAUTH2 Signin Callback
@app.route('/gconnect', methods=['POST'])
def gconnect():
    global linkVisibility
    global buttonVisibility
    global messages

    if request.args.get('state') != login_session['state']:
        print "blew up line 61"
        response = make_response(json.dumps('Invalid state token'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('../client_secrets.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        print "blew up line 72"
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.', 401))
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        print "blew up line 83"
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        print "blew up line 89"
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID.", 401))
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        print "blew up line 95"
        response = make_response(
            json.dumps("Token's client ID doesn't match given application.", 401))
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        print "blew up line 103"
        response = make_response(
            json.dumps("Current user already logged in.", 200))
        response.headers['Content-Type'] = 'application/json'
        return response
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    # flash("you are now logged in as %s"%login_session['username'])
    messages = ['Sign-in Successful']
    signedIn('true')
    print "made it to end"
    return output

@app.route('/logout')
def gdisconnect():
    global messages
    # Only disconnect a connected user.
    signedIn('false')
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
    messages = ['You are now signed out']
    return redirect(url_for('category_list'))

# Site entry point.
# CATEGORY:         List
# REQUIRED PARAMS:  None
# PERMISSIONS:      Public
@app.route('/', methods=['GET', 'POST'])
@app.route('/catalog.html', methods=['GET', 'POST'])
def category_list():
    global linkVisibility
    global buttonVisibility
    global messages
    loginState('catalog.html')
    categories = session.query(Category).all()
    return render_template('catalog.html',
                           categories=categories,
                           showLinks=linkVisibility,
                           showSignIn=buttonVisibility,
                           messages=messages)


# CATEGORY:         Add
# REQUIRED PARAMS:  none
# PERMISSIONS:      Logged-in user
@app.route('/category/add', methods=['GET', 'POST'])
def addCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('category_list'))
    else:
        return render_template('new_category.html')\


# CATEGORY:         Edit
# REQUIRED PARAMS:  Category ID to retrieve current values (GET)
#                   Form data with update info (POST)
# PERMISSIONS:      Logged-in user
@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
            session.add(category)
            session.commit()
        return redirect(url_for('category_list'))
    else:
        return render_template('category_edit.html', category_id=category_id,
                               category_name=category.name)


# CATEGORY:         Delete
# REQUIRED PARAMS:  Category ID to delete
# PERMISSIONS:      Logged-in user
@app.route('/category/<int:category_id>/delete')
def catDelete(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    session.delete(category)
    session.commit()
    return redirect(url_for('category_list'))


# CATEGORY:         JSON Endpoint
# REQUIRED PARAMS:  None
# PERMISSIONS:      Public
@app.route('/categories/JSON')
def categoryListJSON():
    categories = session.query(Category).all()
    return jsonify(category_list=[i.serialize for i in categories])

# ITEMS:            List
# REQUIRED PARAMS:  Category ID to list items from
# PERMISSIONS:      Public
@app.route('/category/<int:category_id>/items')
def itemList(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    categoryitems = session.query(CategoryItem)\
        .filter_by(category_id = category_id).all()
    return render_template('items_in_category.html',
                           category_id=category_id,
                           categoryname=category.name,
                           categoryitems=categoryitems)


# ITEMS:            Add
# REQUIRED PARAMS:  Form data with item info
# PERMISSIONS:      Logged-in user
@app.route('/item/<int:category_id>/add', methods=['GET', 'POST'])
def addItem(category_id):
    if request.method == 'POST':
        category = session.query(Category).filter_by(id=category_id).one()
        new_item=CategoryItem(title=request.form['title'],
                              description=request.form['description'],
                              category=category)
        session.add(new_item)
        session.commit()
        return redirect(url_for('itemList', category_id=category_id))
    else:
        category = session.query(Category).filter_by(id=category_id).one()
        return render_template(
            'new_category_item.html',
            category_id=category_id,
            category_name=category.name)

# ITEMS: Edit
# REQUIRED PARAMS:  Item ID to display current item info in form (GET)
#                   Form data with updated item info (POST)
# PERMISSIONS:      Logged-in user
@app.route('/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def itemEdit(item_id):
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    category_id = item.category_id
    if request.method == 'POST':
        if request.form['title']:
            item.title = request.form['title']
        if request.form['description']:
            item.description = request.form['description']
        session.add(item)
        session.commit()
        return redirect(url_for('itemList', category_id=category_id))
    else:
        return render_template('edit_item.html',
                        item_id=item.id,
                        item_title=item.title,
                        item_description=item.description)


# ITEMS:            Delete
# REQUIRED PARAMS:  Item ID to delete
# PERMISSIONS:      Logged-in user
@app.route('/item/<int:categoryitems_id>/delete')
def itemDelete(categoryitems_id):
    item = session.query(CategoryItem).filter_by(id=categoryitems_id).one()
    session.delete(item)
    session.commit()
    return redirect(url_for('category_list'))



# ITEMS:            JSON Endpoint
# REQUIRED PARAMS:  Category ID for items to list as JSON
# PERMISSIONS:      Public
@app.route('/items/<int:category_id>/JSON')
def itemlistJSON(category_id):
    categoryitems = session.query(CategoryItem)\
        .filter_by(category_id=category_id).all()
    return jsonify(items_list=[i.serialize for i in categoryitems])


def loginState(source):
    global linkVisibility
    global messages
    global buttonVisibility
    print 'Source: ' + source
    print 'Link: ' + linkVisibility
    print 'Buttons: ' + buttonVisibility
    print 'Messages: '
    for i in messages:
        print i

def signedIn(status):
    global buttonVisibility
    global linkVisibility
    if status == 'true':
        linkVisibility = 'show'
        buttonVisibility = 'hide'
    else:
        linkVisibility = 'hide'
        buttonVisibility = 'true'
    loginState('signedIn ' + status)


def get_flashed_messages():
    global messages
    displayMessages = messages
    messages = []
    return displayMessages

if __name__ == '__main__':
    app.debug = True
    app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                             for x in xrange(32))
    app.run(host='0.0.0.0', port=8000)
