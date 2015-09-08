from flask import Blueprint, Flask, render_template, redirect, url_for

# import the mod_catalog package which contains the catalog operations
from catalog_main.mod_catalog.controllers import mod_catalog as catalog_module

# instantiate the app as a Flask app
app = Flask(__name__)

# configure the app from the config.py file
app.config.from_object('config')

# set up default 404 page
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# register the catalog operations in the app namespace
app.register_blueprint(catalog_module)

# configure the default route to redirect to /catalog/
# there is a route in the catalog_module that catches
# defaults to /catalog/ and returns /catalog/catalog.html
@app.route('/', methods=['GET'])
def show_list():
    return redirect('/catalog/')