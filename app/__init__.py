from flask import Blueprint, Flask, render_template, redirect, url_for

from app.mod_catalog.controllers import mod_catalog as catalog_module

app = Flask(__name__)

app.config.from_object('config')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

app.register_blueprint(catalog_module)

@app.route('/', methods=['GET'])
def show_list():
    return redirect('/catalog/')