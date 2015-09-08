import random
import string
import json
from flask import Blueprint, render_template, request, redirect, url_for, \
    jsonify, make_response, flash
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests

from app.mod_catalog.models import Base, Category, CategoryItem

engine = create_engine('sqlite:///app/mod_db/catalog.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

linkVisibility = 'hide'
buttonVisibility = 'show'
CLIENT_ID = json.loads(
    open('../client_secrets.json', 'r').read())['web']['client_id']

mod_catalog = Blueprint('mod_catalog', __name__, url_prefix='/catalog')


# Site entry point.
# CATEGORY:         List
# REQUIRED PARAMS:  None
# PERMISSIONS:      Public
@mod_catalog.route('/', methods=['GET', 'POST'])
@mod_catalog.route('/catalog.html')
def category_list():
    global linkVisibility
    global buttonVisibility
    global login_session
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
                    for x in xrange(32))
    login_session['state'] = state
    #loginState('catalog.html')
    categories = session.query(Category).all()
    return render_template('catalog/catalog.html',
                           categories=categories,
                           showLinks=linkVisibility,
                           showSignIn=buttonVisibility,
                           state=state)


# OAUTH2 Signin Callback
@mod_catalog.route('/gconnect', methods=['POST'])
def gconnect():
    global linkVisibility
    global buttonVisibility
    global login_session
    #loginState('gconnect start')
    #print('request state: ' + request.args.get('state'))
    if request.args.get('state') != login_session['state']:
        #print "blew up line 61"
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
        #print "blew up line 72"
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
        #print "blew up line 83"
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        #print "blew up line 89"
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID.", 401))
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        #print "blew up line 95"
        response = make_response(
            json.dumps("Token's client ID doesn't match given application.", 401))
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        #print "blew up line 103"
        response = make_response(
            json.dumps("Current user already logged in.", 200))
        flash("You are already logged in.")
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

    output = 'Welcome, '
    output += login_session['username']
    output += '! You are now signed in.'
    flash(output)
    signedIn('true')
    #loginState('gconnect')
    #print "made it to end"
    return output


@mod_catalog.route('/logout')
def gdisconnect():
    # Only disconnect a connected user.
    global login_session
    signedIn('false')
    #loginState('gdisconnect at beginning')
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('No user is logged in.'), 401)
        response.headers['Content-Type'] = 'application/json'
        flash("No user is logged in")
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    #print('here')
    if result['status'] == '200':
        # Reset the user's session.
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
    flash('You have successfully signed out')
    return redirect(url_for('.category_list'))


# CATEGORY:         Add
# REQUIRED PARAMS:  none
# PERMISSIONS:      Logged-in user
@mod_catalog.route('/category/add', methods=['GET', 'POST'])
def addCategory():
    global linkVisibility
    global buttonVisibility
    global login_session
    #loginState('addCategory')
    if 'username' not in login_session:
        flash("You must be logged in to use that page")
        return redirect(url_for('.category_list'))
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        flash('Category added successfully')
        return redirect(url_for('.category_list'))
    else:
        return render_template('catalog/new_category.html',
                               showLinks=linkVisibility,
                               showSignIn=buttonVisibility,
                               state=login_session['state'])

    
# CATEGORY:         Edit
# REQUIRED PARAMS:  Category ID to retrieve current values (GET)
#                   Form data with update info (POST)
# PERMISSIONS:      Logged-in user
@mod_catalog.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    global linkVisibility
    global buttonVisibility
    #loginState('editCategory')
    if 'username' not in login_session:
        flash("You must be logged in to use that page")
        return redirect(url_for('.category_list'))
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
            session.add(category)
            session.commit()
            flash('Category updated')
        return redirect(url_for('.category_list'))
    else:
        return render_template('catalog/category_edit.html',
                               category_id=category_id,
                               category_name=category.name,
                               showLinks=linkVisibility,
                               showSignIn=buttonVisibility,
                               state=login_session['state'])


# CATEGORY:         Delete
# REQUIRED PARAMS:  Category ID to delete
# PERMISSIONS:      Logged-in user
@mod_catalog.route('/category/<int:category_id>/delete')
def catDelete(category_id):
    #loginState('catDelete')
    if 'username' not in login_session:
        flash("You must be logged in to use that page")
        return redirect(url_for('.category_list'))
    category = session.query(Category).filter_by(id=category_id).one()
    session.delete(category)
    session.commit()
    flash('Category has been deleted')
    return redirect(url_for('.category_list'))


# CATEGORY:         JSON Endpoint
# REQUIRED PARAMS:  None
# PERMISSIONS:      Public
@mod_catalog.route('/categories/JSON')
def categoryListJSON():
    categories = session.query(Category).all()
    return jsonify(category_list=[i.serialize for i in categories])


# ITEMS:            List
# REQUIRED PARAMS:  Category ID to list items from
# PERMISSIONS:      Public
@mod_catalog.route('/category/<int:category_id>/items')
def itemList(category_id):
    global linkVisibility
    global buttonVisibility
    #loginState('itemList')
    category = session.query(Category).filter_by(id=category_id).one()
    categoryitems = session.query(CategoryItem) \
        .filter_by(category_id = category_id).all()
    return render_template('catalog/items_in_category.html',
                           category_id=category_id,
                           categoryname=category.name,
                           categoryitems=categoryitems,
                           showLinks=linkVisibility,
                           showSignIn=buttonVisibility,
                           state=login_session['state'])

# ITEMS:            Add
# REQUIRED PARAMS:  Form data with item info
# PERMISSIONS:      Logged-in user
@mod_catalog.route('/item/<int:category_id>/add', methods=['GET', 'POST'])
def addItem(category_id):
    global linkVisibility
    global buttonVisibility
    #loginState('addItem')
    if 'username' not in login_session:
        flash("You must be logged in to use that page")
        return redirect(url_for('.category_list'))
    if request.method == 'POST':
        category = session.query(Category).filter_by(id=category_id).one()
        new_item = CategoryItem(title=request.form['title'],
                              description=request.form['description'],
                              category=category)
        session.add(new_item)
        session.commit()
        flash('Item added successfully')
        return redirect(url_for('.itemList', category_id=category_id))
    else:
        category = session.query(Category).filter_by(id=category_id).one()
        return render_template(
            'catalog/new_category_item.html',
            category_id=category_id,
            category_name=category.name,
            showLinks=linkVisibility,
            showSignIn=buttonVisibility,
            state=login_session['state'])

# ITEMS: Edit
# REQUIRED PARAMS:  Item ID to display current item info in form (GET)
#                   Form data with updated item info (POST)
# PERMISSIONS:      Logged-in user
@mod_catalog.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def itemEdit(item_id):
    global linkVisibility
    global buttonVisibility
    #loginState('itemEdit')
    if 'username' not in login_session:
        flash("You must be logged in to use that page")
        return redirect(url_for('.category_list'))
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    category_id = item.category_id
    if request.method == 'POST':
        if request.form['title']:
            item.title = request.form['title']
        if request.form['description']:
            item.description = request.form['description']
        session.add(item)
        session.commit()
        flash('Item updated successfully')
        return redirect(url_for('.itemList', category_id=category_id))
    else:
        return render_template('catalog/edit_item.html',
                               item_id=item.id,
                               item_title=item.title,
                               item_description=item.description,
                               showLinks=linkVisibility,
                               showSignIn=buttonVisibility,
                               state=login_session['state'])


# ITEMS:            Delete
# REQUIRED PARAMS:  Item ID to delete
# PERMISSIONS:      Logged-in user
@mod_catalog.route('/item/<int:categoryitems_id>/delete')
def itemDelete(categoryitems_id):
    #loginState('itemDelete')
    if 'username' not in login_session:
        flash("You must be logged in to use that page")
        return redirect(url_for('.category_list'))
    item = session.query(CategoryItem).filter_by(id=categoryitems_id).one()
    session.delete(item)
    session.commit()
    flash('Item deleted')
    return redirect(url_for('.category_list'))



# ITEMS:            JSON Endpoint
# REQUIRED PARAMS:  Category ID for items to list as JSON
# PERMISSIONS:      Public
@mod_catalog.route('/items/<int:category_id>/JSON')
def itemlistJSON(category_id):
    categoryitems = session.query(CategoryItem) \
        .filter_by(category_id=category_id).all()
    return jsonify(items_list=[i.serialize for i in categoryitems])


def loginState(source):
    global linkVisibility
    global buttonVisibility
    global login_session
    print 'Source: ' + source
    print 'Link: ' + linkVisibility
    print 'Buttons: ' + buttonVisibility
    print 'Login state: ' + login_session['state']

def signedIn(status):
    global buttonVisibility
    global linkVisibility
    if status == 'true':
        linkVisibility = 'show'
        buttonVisibility = 'hide'
    else:
        linkVisibility = 'hide'
        buttonVisibility = 'true'
    #loginState('signedIn ' + status)


