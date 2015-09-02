__author__ = 'Greg'

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

@app.route('/login')
@app.route('/gconnect', methods=['POST'])
@app.route('/logout')
@app.route('/', methods=['GET', 'POST'])
@app.route('/catalog.html', methods=['GET', 'POST'])
@app.route('/category/add', methods=['GET', 'POST'])
@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@app.route('/category/<int:category_id>/delete')
@app.route('/categories/JSON')
@app.route('/category/<int:category_id>/items')
@app.route('/item/<int:category_id>/add', methods=['GET', 'POST'])
@app.route('/item/<int:item_id>/edit',
@app.route('/item/<int:categoryitems_id>/delete')
@app.route('/items/<int:category_id>/JSON')