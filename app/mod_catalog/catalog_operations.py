__author__ = 'Greg'

from flask import Blueprint, render_template, request, redirect, url_for, \
    jsonify, g, session, flash

mod_catalog = Blueprint('catalog', __name__, url_prefix='/')

@mod_catalog.route('catalog.html', methods=['GET', 'POST'])

def sayHello():
    return render_template('hello.html', name="Greg")
