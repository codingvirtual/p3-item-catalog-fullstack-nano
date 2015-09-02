__author__ = 'Greg'

from flask import Flask, render_template, request, redirect, url_for, jsonify

class CatalogOperations:

    name = ""

    def __init__(self, name):
        self.name = name

    def sayHello(self):
        return render_template('hello.html', name=self.name)
