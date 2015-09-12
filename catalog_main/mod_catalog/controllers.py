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

# import database model classes
from catalog_main.mod_catalog.models import Base, Category, CategoryItem

# create connection to database
engine = create_engine('sqlite:///catalog_main/mod_db/catalog.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# flags that influence the visibility of links that should only be
# available to users that are signed in.
# NOTE: this is a very light-weight way to do this. It would probably
# be better to use the login status to choose the right template to
# return and only return a page that has the right set of buttons (or
# lacks them accordingly)
linkVisibility = 'hide'
buttonVisibility = 'show'

# Retrive the Google client id from a private file located "above" the
# project root. NOTE: you must have the JSON download from Google
# stored one level above the project and the file must be named
# client_secrets.json in order for the application to run correctly.
# The client id is used by Google to allow users to log in to this
# app using their Google sign-in.
CLIENT_ID = json.loads(
    open('../client_secrets.json', 'r').read())['web']['client_id']

# Register this module as a Blueprint.
mod_catalog = Blueprint('mod_catalog', __name__, url_prefix='/catalog')


# Site entry point.
# CATEGORY:         List
# REQUIRED PARAMS:  None
# PERMISSIONS:      Public
# This is the main block for rendering the default home page for the
# site.
@mod_catalog.route('/', methods=['GET', 'POST'])
@mod_catalog.route('/catalog.html')
def category_list():
    # use 'global' keyword to enable editing of the login_session dictionary
    global login_session

    # Create a state value from random characters. This value is used to
    # prevent request forgeries
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
                    for x in xrange(32))
    # record the value in the login_session dictionary using the 'state' key
    login_session['state'] = state

    # Query the database for the full list of all categories
    categories = session.query(Category).all()

    # Render the template that lists the categories and pass in the
    # categories, visibility indicators, and the state variable.
    return render_template('catalog/catalog.html',
                           categories=categories,
                           showLinks=linkVisibility,
                           showSignIn=buttonVisibility,
                           state=state,
                           CLIENT_ID=CLIENT_ID)


# OAUTH2 Signin Callback
# CATEGORY:         Authorization
# REQUIRED PARAMS:  None
# PERMISSIONS:      Public
# This block is executed when the user clicks on the Google Sign-In button.
@mod_catalog.route('/gconnect', methods=['POST'])
def gconnect():
    # use the 'global' keyword so that these values can be changed below
    global linkVisibility
    global buttonVisibility
    global login_session

    # Extract the 'state' value from the request arguments and compare to
    # our stored state. This ensures that request forgery hasn't taken place.
    if request.args.get('state') != login_session['state']:
        # The states either don't match or one isn't present at all,
        # so return a 401 and exit.
        response = make_response(json.dumps('Invalid state token'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # The state tokens match, so extract the data from the request
    code = request.data
    try:
        # Attempt the OAuth flow using the client secrets file
        oauth_flow = flow_from_clientsecrets('../client_secrets.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # Execute the OAuth request. The result should be a set of credentials
        # if the exchange was successful.
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        # There was an error upgrading the login code for session token
        # Create a response with a 401 and return it.
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.', 401))
        response.headers['Content-Type'] = 'application/json'
        return response

    # At this point, we have a valid access token so extract it.
    access_token = credentials.access_token

    # go fetch the user's info from the Google+ API's
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()

    # Execute the request. The result will contain the user's info if
    # successful.
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        # There was a problem retrieving the user info. Return a 500
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # At this point, we have fully authenticated the user and retrieved their
    # info from Google+. Now extract their GPlus ID from the credentials
    # we received earlier...
    gplus_id = credentials.id_token['sub']

    # and compare that id to the ID that the user info from Google contained.
    # They should match.
    if result['user_id'] != gplus_id:
        # For some reason, there was not a match, so return a 401 error.
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID.", 401))
        response.headers['Content-Type'] = 'application/json'
        return response

    # Now make sure the token info for the client ID matches our client_ID
    if result['issued_to'] != CLIENT_ID:
        # They didn't match (which should not happen), so return a 401
        response = make_response(
            json.dumps("Token's client ID doesn't match given application.", 401))
        response.headers['Content-Type'] = 'application/json'
        return response

    # Extract the value of any stored credentials and user ID from the
    # active session. This will allow us to check if there is a user
    # already logged in, in which case we abort this flow.
    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    # If there is a stored token and a stored gplus id, then someone
    # is already logged in.
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        # User already logged in, so return a 200 and exit.
        response = make_response(
            json.dumps("Current user already logged in.", 200))

        # Queue up a flash so that when the next page displays, the user
        # sees an informational message letting them know they are already
        # logged in.
        flash("You are already logged in.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # At this point in the flow, the user is now fully logged in and we
    # need to store the relevant info for other pages to use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Now we are going to go fetch the user's name and picture
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}

    # This is the actual call to fetch the data
    answer = requests.get(userinfo_url, params=params)

    # Convert the JSON that is returned to a dictionary
    data = answer.json()

    # Extract the fields we want.
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']

    # Set up a "success" message to show when the login flow is done.
    output = 'Welcome, '
    output += login_session['username']
    output += '! You are now signed in.'

    # Queue the message
    flash(output)

    # call utility function that sets the correct values for the various
    # flags and status variables used throughout the app
    signedIn('true')
    return output

# OAUTH2 Sign-out function
# CATEGORY:         Authorization
# REQUIRED PARAMS:  None
# PERMISSIONS:      Logged-in User
# This block is executed when the user clicks on the Logout button.
@mod_catalog.route('/logout')
def gdisconnect():
    # use the 'global' keyword so we can unset various keys from the
    # login_session dictionary
    global login_session

    # see if there is an existing access token. If not, then there is
    # no user logged in so we can abort the process and return a 401
    if login_session.get('access_token') is None:
        response = make_response(
            json.dumps('No user is logged in.'), 401)
        response.headers['Content-Type'] = 'application/json'

        # Queue an informational message to be displayed when the return
        # page is rendered
        flash("No user is logged in")
        return response

    # There is an active user if we make it to this point, so first we need
    # to revoke the access token so it cannot be used further.
    # Set up the request
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
          login_session['access_token']
    h = httplib2.Http()

    # Actually make the request to revoke the token
    result = h.request(url, 'GET')[0]

    # Now confirm we got a 200 OK back from Google, which means we did
    # successfully revoke the token
    if result['status'] == '200':
        # Reset the relevant fields of the session dictionary
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']

        # call utility funciton to change the flags for the app.
        signedIn('false')

        # set up response
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
    else:
        # For whatever reason, the given token was invalid, so return an error
        # 400.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'

    # At this point, the user has been logged out. Queue a message telling them
    flash('You have successfully signed out')
    return redirect(url_for('.category_list'))


# CATEGORY:         Add
# REQUIRED PARAMS:  none
# PERMISSIONS:      Logged-in user
# This block presents a page that allows the user to add a new category
# to the database.
@mod_catalog.route('/category/add', methods=['GET', 'POST'])
def addCategory():
    # Validate that there is a user logged in. This prevents the page
    # from being accessed via direct URL
    if 'username' not in login_session:
        # Queue a message telling them they must be logged in to use this page
        flash("You must be logged in to use that page")

        # send the user back to the main page for the site
        return redirect(url_for('.category_list'))

    # If we got here via a POST, that means the user has filled out the form
    # on the page and submitted it, so we process the add to the database.
    if request.method == 'POST':
        #Extract the category name from the form.
        newCategory = Category(name=request.form['name'])

        # Add it to the database and commit
        session.add(newCategory)
        session.commit()

        # Queue a success message and send them back to the main page.
        flash('Category added successfully')
        return redirect(url_for('.category_list'))

    # The request is a GET, which indicates that we need to show them the
    # form so they can fill it out
    else:
        # Render the new category form and pass in the relevant variables
        return render_template('catalog/new_category.html',
                               showLinks=linkVisibility,
                               showSignIn=buttonVisibility,
                               state=login_session['state'])

    
# CATEGORY:         Edit
# REQUIRED PARAMS:  Category ID to retrieve current values (GET)
#                   Form data with update info (POST)
# PERMISSIONS:      Logged-in user
# This block allows the user to edit the name of a given category.
@mod_catalog.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    # verify there is a logged-in user.
    if 'username' not in login_session:
        # no logged-in user, so queue a message and return them to the main page
        flash("You must be logged in to use that page")
        return redirect(url_for('.category_list'))

    # Grab the category info from the database based on the category's id
    category = session.query(Category).filter_by(id=category_id).one()

    # if we got here with a POST request, that means the user has filled out
    # the form and we need to process the update to the database
    if request.method == 'POST':
        # It's a POST< so there should be form data to extract
        if request.form['name']:

            # extract the new category name and update the database
            category.name = request.form['name']
            session.add(category)
            session.commit()

            # queue a success message
            flash('Category updated')
        return redirect(url_for('.category_list'))

    # got here via GET, so need to show the user the form. Pass in the
    # relevant category details to prepopulate the form with those values.
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
# This block is executed when the user clicks the Delete button for a given
# category, which they should only be able to see (or do) if they are a
# logged-in user.
@mod_catalog.route('/category/<int:category_id>/delete')
def catDelete(category_id):
    # confirm they are logged in
    if 'username' not in login_session:

        # User is not logged in, so queue a message and return them
        # to the main page
        flash("You must be logged in to use that page")
        return redirect(url_for('.category_list'))

    # Valid user, so extract the category object from the database
    # so we can then pass it to the delete function.
    category = session.query(Category).filter_by(id=category_id).one()

    # Delete the category.
    session.delete(category)
    session.commit()

    # Queue a success message and return them to the main page
    flash('Category has been deleted')
    return redirect(url_for('.category_list'))


# CATEGORY:         JSON Endpoint
# REQUIRED PARAMS:  None
# PERMISSIONS:      Public
# This block provides a JSON endpoint for the list of categories in the db
@mod_catalog.route('/categories/JSON')
def categoryListJSON():
    # fetch the list of categories
    categories = session.query(Category).all()

    # return it as json
    return jsonify(category_list=[i.serialize for i in categories])


# ITEMS:            List
# REQUIRED PARAMS:  Category ID to list items from
# PERMISSIONS:      Public
# This block is executed when the user clicks on a category name in order
# to view a list of items in that category.
@mod_catalog.route('/category/<int:category_id>/items')
def itemList(category_id):
    # Get the category first using the category id
    category = session.query(Category).filter_by(id=category_id).one()

    # now go fetch the items for this category from the dab
    categoryitems = session.query(CategoryItem) \
        .filter_by(category_id = category_id).all()

    # render the results by passing the relevant data to the template
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
# This block is executed when the user wants to add an item to a category.
@mod_catalog.route('/item/<int:category_id>/add', methods=['GET', 'POST'])
def addItem(category_id):
    # Confirm a valid user is logged in
    if 'username' not in login_session:
        # No valid user, so queue a message and return them to the main page
        flash("You must be logged in to use that page")
        return redirect(url_for('.category_list'))

    # at this point we do have a valid user.
    # Check if the request was a POST which means the user has submitted
    # the form to add the new item
    if request.method == 'POST':
        # Request is a POST, so process adding a new item
        # Get the category info first so we can relate the item to it
        category = session.query(Category).filter_by(id=category_id).one()

        # Create the item object from the form data
        new_item = CategoryItem(title=request.form['title'],
                              description=request.form['description'],
                              category=category)

        # add to the database
        session.add(new_item)
        session.commit()

        # Queue a success message and return them to the list of items
        flash('Item added successfully')
        return redirect(url_for('.itemList', category_id=category_id))

    # The request is a GET, so need to display the form that lets them
    # input the fields to add a new item.
    else:
        # Extract the category so we can display its title in the
        # template (so the user knows which category they are adding an
        # item to).
        category = session.query(Category).filter_by(id=category_id).one()

        # return the template with the category info passed in
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
# This block is executed when a user clicks the Edit button next to an
# item in the item list for a given category. The user should only be
# able to see (and do) the edit if they are logged in.
@mod_catalog.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def itemEdit(item_id):
    # Validate we have a logged-in user
    if 'username' not in login_session:
        # No user, so queue a message and return them to the main page
        flash("You must be logged in to use that page")
        return redirect(url_for('.category_list'))

    # We have a valid user, so continue.
    # Pull the item info from the database using the item id
    item = session.query(CategoryItem).filter_by(id=item_id).one()

    # extract the category id
    category_id = item.category_id

    # Check if the request was a POST (which would contain form data to
    # process) or a GET (which indicates we need to display the edit form)
    if request.method == 'POST':
        # It's a POST, so go get the form field info from the request and
        # update the previously-retrieved item object with the new values.
        if request.form['title']:
            item.title = request.form['title']
        if request.form['description']:
            item.description = request.form['description']

        # update the db with the modified item
        session.add(item)
        session.commit()

        # Queue a success message and return the user to the list of
        # items for this category.
        flash('Item updated successfully')
        return redirect(url_for('.itemList', category_id=category_id))

    else:
        # It's a GET request, so render the form template and pass in
        # the appropriate values for the form defaults, etc.
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
# This block is executed when the user clicks the Delete button next to
# an item in the item list. There should be a valid user in order to see
# (or do) this edit page.
@mod_catalog.route('/item/<int:categoryitems_id>/delete')
def itemDelete(categoryitems_id):
    # Check for a valid user
    if 'username' not in login_session:
        # No user, so queue a message and return them to the main page
        flash("You must be logged in to use that page")
        return redirect(url_for('.category_list'))

    # Valid user, so continue
    # Extract the item to be deleted from the database
    item = session.query(CategoryItem).filter_by(id=categoryitems_id).one()

    # use that item object to delete the item
    session.delete(item)
    session.commit()

    # Queue a message that the item was deleted and return the user to the
    # main page.
    flash('Item deleted')
    return redirect(url_for('.category_list'))



# ITEMS:            JSON Endpoint
# REQUIRED PARAMS:  Category ID for items to list as JSON
# PERMISSIONS:      Public
# This block provides a JSON endpoint for the list of items in a given
# category.
@mod_catalog.route('/items/<int:category_id>/JSON')
def itemlistJSON(category_id):
    # Extract the items from the db based on the category ID
    categoryitems = session.query(CategoryItem) \
        .filter_by(category_id=category_id).all()

    # Return the results as JSON
    return jsonify(items_list=[i.serialize for i in categoryitems])

# Utility function that sets the state of the visibility flags
def signedIn(status):
    global buttonVisibility
    global linkVisibility
    # Set the flags based on whether or not there is a logged-in user
    if status == 'true':
        # user IS logged in. Show buttons or links to restricted content,
        # show the Logout button, and hidee the G+ login button
        linkVisibility = 'show'
        buttonVisibility = 'hide'
    else:
        # user is not logged in. Do NOT show buttons or links to restricted
        # content, hide the logout button, but show the G+ login button
        linkVisibility = 'hide'
        buttonVisibility = 'true'


