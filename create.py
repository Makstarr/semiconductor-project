import os
from sqlalchemy import and_
from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://ewrsgiutbrhrwo:517f2f57b484be1b55cf9529a2918fea0264322eb94fd63a0a0363e6a5ba9cb8@ec2-54-247-189-1.eu-west-1.compute.amazonaws.com:5432/d6kq1fgt1cafb7"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():

    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()
