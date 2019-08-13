from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Semiconductor(db.Model):
    __tablename__ = "semiconductors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    m_dn = db.Column(db.Float, nullable=False)
    m_dp = db.Column(db.Float, nullable=False)
    epsilon = db.Column(db.Float, nullable=False)
    mu_n_300 = db.Column(db.Float, nullable=False)
    mu_p_300 = db.Column(db.Float, nullable=False)##

class Parameters(db.Model):
    __tablename__ = "parameters"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    concentration =  db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Integer, nullable=False)
    n = db.Column(db.Float, nullable=False)
    reverse_temp = db.Column(db.Float, nullable=False)
    lnn = db.Column(db.Float, nullable=False)
    ni = db.Column(db.Float, nullable=False)
    Fi = db.Column(db.Float, nullable=False)
    F = db.Column(db.Float, nullable=False)
    Eg = db.Column(db.Float, nullable=False)
    mu = db.Column(db.Float, nullable=False)
