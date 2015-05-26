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

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Site entry point.
# CATEGORY:         List
# REQUIRED PARAMS:  None
# PERMISSIONS:      Public
@app.route('/')
@app.route('/catalog.html')
def category_list():
    categories = session.query(Category).all()
    return render_template('catalog.html', categories=categories)


# CATEGORY:         Add
# REQUIRED PARAMS:  none
# PERMISSIONS:      Logged-in user
@app.route('/new_category.html', methods = ['GET','POST'])
def addCategory():
    if request.method == 'POST':
        newCategory = Category(name = request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('category_list'))
    else:
        return render_template('new_category.html')\


# CATEGORY:         Edit
# REQUIRED PARAMS:  Category ID to retrieve current values (GET)
#                   Form data with update info (POST)
# PERMISSIONS:      Logged-in user
@app.route('/category/<int:category_id>/edit', methods=['GET','POST'])


# CATEGORY:         Delete
# REQUIRED PARAMS:  Category ID to delete
# PERMISSIONS:      Logged-in user
@app.route('/category/<int: category_id>/delete', methods=['DELETE'])


# CATEGORY:         JSON Endpoint
# REQUIRED PARAMS:  None
# PERMISSIONS:      Public
@app.route('/categories/JSON')


# ITEMS:            List
# REQUIRED PARAMS:  Category ID to list items from
# PERMISSIONS:      Public
@app.route('/category/<int:category_id>/items')
def itemList(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    categoryitems = session.query(CategoryItem).filter_by(category_id = category_id).all()
    return render_template('items_in_category.html', categoryname=category.name, categoryitems=categoryitems)


# ITEMS:            Add
# REQUIRED PARAMS:  Form data with item info
# PERMISSIONS:      Logged-in user
@app.route('/item/<int:category_id>/add', methods=['POST'])


# ITEMS: Edit
# REQUIRED PARAMS:  Item ID to display current item info in form (GET)
#                   Form data with updated item info (POST)
# PERMISSIONS:      Logged-in user
@app.route('/item/<int:categoryitems_id>/edit', methods=['GET','POST'])


# ITEMS:            Delete
# REQUIRED PARAMS:  Item ID to delete
# PERMISSIONS:      Logged-in user
@app.route('/item/<int:categoryitems_id>/delete', methods=['DELETE'])



# ITEMS:            JSON Endpoint
# REQUIRED PARAMS:  Category ID for items to list as JSON
# PERMISSIONS:      Public
@app.route('/items/<int:category_id>/JSON')
def itemlistJSON(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    categoryitems = session.query(CategoryItem).filter_by(category_id = category_id).all()
    return jsonify(CategoryItems = [i.serialize for i in categoryitems])


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
