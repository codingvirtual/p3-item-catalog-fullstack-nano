from flask import Flask, render_template, request, redirect, url_for, jsonify
import jinja2

app = Flask(__name__)

import random, string

from catalog_operations import CatalogOperations

catalogOps = CatalogOperations("Bill")


@app.route('/', methods=['GET', 'POST'])
def doHome():
    return catalogOps.sayHello()

# @app.route('/login')
# @app.route('/gconnect', methods=['POST'])
# @app.route('/logout')
# @app.route('/catalog.html', methods=['GET', 'POST'])
# @app.route('/category/add', methods=['GET', 'POST'])
# @app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
# @app.route('/category/<int:category_id>/delete')
# @app.route('/categories/JSON')
# @app.route('/category/<int:category_id>/items')
# @app.route('/item/<int:category_id>/add', methods=['GET', 'POST'])
# @app.route('/item/<int:item_id>/edit',
# @app.route('/item/<int:categoryitems_id>/delete')
# @app.route('/items/<int:category_id>/JSON')


if __name__ == '__main__':
    app.debug = True
    app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                         for x in xrange(32))
    app.run(host='0.0.0.0', port=8000)