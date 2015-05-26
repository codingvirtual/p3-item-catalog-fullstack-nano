from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def categoryList():
    categories = session.query(Category).all()
    return render_template('catalog.html', categories=categories)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)

