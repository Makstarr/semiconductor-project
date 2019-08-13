import csv
import os

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

class GaAs():
    name = 'GaAs'
    m_dn = 0.067
    m_dp = 0.45
    epsilon = 13.1
    mu_n_300 = 8000
    mu_p_300 = 400
    xl = 55


# Parameters of Si
class Si():
    name = 'Si'
    m_dn = 1.08
    m_dp = 0.59
    epsilon = 11.7
    mu_n_300 = 1350
    mu_p_300 = 450
    xl = 130                      # Нужно табличное значение


# Parameters of Ge
class Ge():
    name = 'Ge'
    m_dn = 0.56
    m_dp = 0.37
    epsilon = 16.3
    mu_n_300 = 3900
    mu_p_300 = 1900
    xl = 58  # Нужно табличное значение
semiconductors=[]
def main():
    ge=Ge()
    si=Si()
    gaas=GaAs()
    semiconductors.append(ge)
    semiconductors.append(si)
    semiconductors.append(gaas)

    for semiconductor in semiconductors:
        sc = Semiconductor(name=semiconductor.name, m_dn = semiconductor.m_dn, m_dp = semiconductor.m_dp, epsilon = semiconductor.epsilon, mu_n_300 = semiconductor.mu_n_300, mu_p_300 = semiconductor.mu_p_300)
        db.session.add(sc)
        print(f"Added semiconductor {semiconductor.name} with m_dn = {semiconductor.m_dn}")
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()
