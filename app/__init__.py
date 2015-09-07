from flask import Blueprint, Flask, render_template

from app.mod_catalog.catalog_operations import mod_catalog as catalog_module

app = Flask(__name__)

app.config.from_object('config')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

app.register_blueprint(catalog_module)

