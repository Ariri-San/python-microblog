# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 13:36:02 2022

@author: Kenobi-Kylo
"""

import datetime
from flask import Flask, redirect, url_for, render_template, request
from pymongo import MongoClient

def create_app():

    app = Flask(__name__)
    client = MongoClient("mongodb+srv://kenobi:13815437@microblog-1.tk0zu8o.mongodb.net/test")
    app.db = client.microblog


    entries = [i for i in app.db.entries.find()]

    @app.route("/", methods=["GET", "POST"])
    def home():
        if request.method == "POST" and request.form["id"] == "":
            entry_title = request.form.get("title")
            entry_content = request.form.get("content")
            formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")
            show_date = datetime.datetime.strptime(formatted_date, "%Y-%m-%d").strftime("%b %d")
            entry = {
                "entry_title" : entry_title,
                "entry_content" : entry_content,
                "formatted_date" : formatted_date,
                "show_date" : show_date
            }
            entries.append(entry)
            app.db.entries.insert_many([entry])
        
        elif request.method == "POST" and request.form["id"] != "":
            for i in entries:
                if str(i) == request.form["id"]:
                    entries.remove(i)
                    app.db.entries.delete_many(i)
        
        return render_template("home.html", entries=entries)
    
    return app
