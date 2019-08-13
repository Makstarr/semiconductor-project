from flask import Flask, render_template, jsonify, request
from models import *
from count import *
from sqlalchemy import and_
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.route("/")
def index():
    semiconductors = Semiconductor.query.all()
    return render_template("index.html", semiconductors=semiconductors)
@app.route("/count", methods=["POST","GET"])
def count():
    """Count"""
    if request.method == "GET":
        semiconductors = Semiconductor.query.all()
        return render_template("index.html",semiconductors=semiconductors )
    if request.method == "POST":
        # Get form information.
        semiconductor_id = request.form.get("semiconductor_id")
        name = Semiconductor.query.filter_by(id=semiconductor_id).first().name
        concentration = float(request.form.get("concentration"))
        Ea = float(request.form.get("Ea"))
        type = request.form.get("type")
        start = 5
        end = 1000
        # Add parameters
        if Parameters.query.filter(and_(Parameters.name == name, Parameters.concentration == concentration, Parameters.type == type)).count()!= 0:
            parameters = Parameters.query.filter(and_(Parameters.name == name, Parameters.concentration == concentration, Parameters.type == type)).order_by(Parameters.temperature).all()
            return render_template("results.html", parameters=parameters)
        else:
            for temperature in range(start, end, 5):
                F, n, lnn, ni, reverse_temp, Eg, Fi, mu = parameters_count(temperature, name, concentration, Ea, bool(type))
                par = Parameters(type = type, temperature= temperature, reverse_temp = reverse_temp, F = F, Fi = Fi, lnn = lnn, ni= ni, n=n, Eg = Eg,  mu = mu, name=name, concentration=concentration)
                db.session.add(par)
            db.session.commit()
            parameters = Parameters.query.filter(and_(Parameters.name == name, Parameters.concentration == concentration, Parameters.type == type)).all()
            return render_template("results.html", parameters=parameters, type = bool(type))
