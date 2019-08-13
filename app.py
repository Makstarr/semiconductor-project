from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from count import *
import os

app = Flask(__name__)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app.static_folder = 'static'
@app.route("/")
def index():
    class1 = 'class=active'
    return render_template("index.html", class1="class=active")
@app.route("/pn-junction")
def pnjunction():
    class2 = 'class=active'
    return render_template("projects/pn-junction.html",class2=class2)
@app.route("/npn-junction")
def npnjunction():
    class3 = 'class=active'
    return render_template("projects/npn-junction.html",class3=class3)

@app.route("/<string:action>", methods=["POST", "GET"])
def count(action):
    if request.method == "GET":
        return render_template("count.html")
    if request.method == "POST":
        name  = request.form.get("name")
        temperature  = int(request.form.get("temperature"))
        concentration  = request.form.get("concentration")
        type  = request.form.get("type")
        sq = sqr(temperature)
        for x in sq:
            db.execute("INSERT INTO count (name,type,temperature,concentration, sqrt) VALUES (:name, :type, :temperature, :concentration, :sqrt)", {"name": name, "type": type, "temperature": temperature, "concentration": concentration, "sqrt":x})
        db.commit()


        counts = db.execute("SELECT name, type, temperature, concentration, sqrt FROM count").fetchall()
        return render_template("results.html",  counts=counts)
