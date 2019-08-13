from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
import os
import numpy as np
import math, decimal
from scipy.optimize import fsolve

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Constants
q = 1.6e-19
kb = 1.38e-23
k = 1.38e-23 / q  # Ev
N_avagadro = 6e23
v_snd = 343
h = 43.903876e-68
pi = math.pi
me = 9.11e-31

# formulass parameters that independent from material
class formulas:
    def temperature_1(self, concentration, activate_energy, acceptor):
        # Temperature of impurity ionisation
        def func(temperature_1):
            return 3 - concentration * np.exp(activate_energy / k / temperature_1)/ self.Nc(temperature_1)

        # np.log(concentration) + (activate_energy / k / temperature_1) - 1.5 * np.log(temperature_1 * self.m_dn) - 37.208
        ionization_temperature = fsolve(func, 50)    #90
        return ionization_temperature[0]

    def temperature_2(self, concentration, activate_energy, acceptor):
        # Temperature of intrinsic carriers  ionisation
        def func2(temperature_2):
            return self.ni(temperature_2) - concentration * np.sqrt(2)
        self_conduction_temperature = fsolve(func2, 700)    #800
        return self_conduction_temperature[0]

    def Nv(self, temperature):
        # return (2 * ((2 * self.m_dp * pi * me * kb * temperature) / h) ** 1.5) / 1000000
        return 4.82e15 * (self.m_dp ** 1.5) * (temperature ** 1.5)

    def Nc(self, temperature):
        # return (2 * ((2 * self.m_dn * pi * me * kb * temperature) / h) ** 1.5) / 1000000
        return 4.82e15 * (self.m_dn ** 1.5) * (temperature ** 1.5)

    def ni(self, temperature):
        return ((self.Nc(temperature) * self.Nv(temperature)) ** 0.5) * math.exp(
            -1 * self.Eg(temperature) / (2 * temperature * k))

    def n_critical(self, activate_energy, acceptor):
        if acceptor:
            return np.sqrt(1e45) * (self.m_dp * activate_energy) ** 1.5
        else:
            return np.sqrt(1e45) * (self.m_dn * activate_energy) ** 1.5

    def n1(self, temperature, concentration, activate_energy, acceptor):
        if acceptor:
            Nv = self.Nv(temperature)
            return Nv / 4 * np.exp(-1 * activate_energy / (k * temperature)) * (
                        np.sqrt(1 + 8 * concentration / Nv * np.exp(activate_energy / k / temperature)) - 1)
        else:
            return self.Nc(temperature) / 4 * np.exp(-1 * activate_energy / (k * temperature)) * (np.sqrt(1 + 8 * concentration / self.Nc(temperature) * np.exp(activate_energy / k / temperature)) - 1)

    def n2(self, temperature, concentration):
        return (concentration / 2) * (1 + np.sqrt(1 + 4 * self.ni(temperature) ** 2 / concentration ** 2))

    def fi(self, temperature, acceptor):
        if acceptor:
            return k * temperature * np.log((self.m_dp / self.m_dn) ** (3 / 4))
        else:
            return - k * temperature / 2 * np.log((self.Nc(temperature) / self.Nv(temperature)))

    def f1(self, temperature, concentration, activate_energy, acceptor):
        if acceptor:
            return -self.Eg(temperature) / 2 + k * temperature * np.log(self.Nv(temperature) / (
                        (self.Nv(temperature) * np.exp(-activate_energy / (k * temperature)) / 2) * (-1 + np.sqrt(
                    1 + 8 * (concentration / self.Nc(temperature)) * np.exp(activate_energy / (k * temperature))))))
        else:
            return self.Eg(temperature) / 2 - activate_energy + k * temperature * np.log(1 / 4 * (-1 + np.sqrt(
                    1 + 8 * (concentration / self.Nc(temperature)) * np.exp(activate_energy / (k * temperature)))))

    def f2(self, temperature, concentration, activate_energy, acceptor):
        if acceptor:
            return -self.Eg(temperature) / 2 + k * temperature * np.log(self.Nv(temperature) / (concentration / 2 * (1 + np.sqrt(1 + 4 * (self.ni(temperature) ** 2) / (concentration ** 2)))))
        else:
            return self.Eg(temperature) / 2 + k * temperature * np.log(concentration / (2 * self.Nc(temperature))*(1 + np.sqrt(1 + 4 * (self.ni(temperature) ** 2) / (concentration ** 2))))

    def t_max_fermi(self, concentration, acceptor):
        if acceptor:
            return 8.15 * (1 / self.m_dp) * (concentration / 1e18) ** (2 / 3)
        else:
            return 8.15 * (1 / self.m_dn) * (concentration / 1e18) ** (2 / 3)

    def fermi_max(self, concentration, activate_energy, acceptor):
        if acceptor:
            return (self.Eg(self.t_max_fermi(concentration, acceptor)) / 2 -
                    ((self.Eg(self.t_max_fermi(concentration, acceptor)) / 2)
                    - activate_energy)) / 2 - 5.3e-4 * (1 / self.m_dp) * (concentration / 1e18) ** (2 / 3)
        else:
            return (self.Eg(self.t_max_fermi(concentration, acceptor)) / 2 -
                    ((self.Eg(self.t_max_fermi(concentration, acceptor)) / 2)
                    - activate_energy)) / 2 + 5.3e-4 * (1 / self.m_dn) * (concentration / 1e18) ** (2 / 3)

    def mu_thermal_oscillations(self, temperature, acceptor):
        if acceptor:
            return self.mu_p_300 * (temperature / 300) ** -1.5
        else:
            return self.mu_n_300 * (temperature / 300) ** -1.5

    def mu_impurity_atoms(self, temperature, concentration, acceptor):
        b = (16.3 * temperature / 1000) * (2.35e19 / concentration) ** (1 / 3)
        if acceptor:
            return ((3.68e20 / concentration) * (self.epsilon / 16) ** 2) * ((temperature / 300) ** 1.5) * \
                 ((self.m_dp ** 0.5) * np.log10(1 + b ** 2)) ** -1
        else:
            return ((3.68e20 / concentration) * (self.epsilon / 16) ** 2) * ((temperature / 300) ** 1.5) * \
                   ((self.m_dn ** 0.5) * np.log10(1 + b ** 2)) ** -1

    def mu(self, temperature, concentration, acceptor):
            mu_1 = self.mu_thermal_oscillations(temperature, acceptor)
            mu_2 = self.mu_impurity_atoms(temperature, concentration, acceptor)
            return mu_1 * mu_2 / (mu_1 + mu_2)

    def sigma(self, temperature, concentration, activate_energy, acceptor):
        t1 = self.temperature_1(concentration, activate_energy, acceptor)
        t2 = self.temperature_2(concentration, activate_energy, acceptor)
        if acceptor:
            if t1 < temperature < t2:
                return q*concentration*self.mu_p_300
            else:
                return 0
        else:
            if t1 < temperature < t2:
                return q * concentration * self.mu_n_300
            else:
                return 0

    def x(self, temperature, concentration, activate_energy, acceptor, x):
        if x == 'xe':
            if (self.mu(temperature + 1e5, concentration, acceptor)-self.mu(temperature, concentration, acceptor)) < 0:
                xe = 2 * self.sigma(temperature, concentration, activate_energy, acceptor) * k ** 2 * temperature
                return xe
            else:
                xe = 4 * self.sigma(temperature, concentration, activate_energy, acceptor) * k ** 2 * temperature
                return xe
        elif x == 'xl':
            return self.xl
        else:
            if (self.mu(temperature + 1e5, concentration, acceptor)-self.mu(temperature, concentration, acceptor)) < 0:
                xe = 2 * self.sigma(temperature, concentration, activate_energy, acceptor)*k**2 * temperature
                return self.xl + xe
            else:
                xe = 4 * self.sigma(temperature, concentration, activate_energy, acceptor) * k ** 2 * temperature
                return self.xl + xe

    def Rh(self, temperature, concentration, acceptor):
        if acceptor:
            z = 1
        else:
            z = -1
        if (self.mu(temperature + 1e5, concentration, acceptor)-self.mu(temperature, concentration, acceptor)) < 0:
            r = 1.18 * z
            return r / q / concentration / 1e6
        else:
            r = 1.93 * z
            return r / q / concentration / 1e6

    def alpha_t(self, temperature, concentration, acceptor):
        if (self.mu(temperature + 1e5, concentration, acceptor)-self.mu(temperature, concentration, acceptor)) < 0:
            r = 1/2
        else:
            r = -3/2
        if acceptor:
            return k * (5 / 2 - r + np.log(self.Nv(temperature) / concentration))
        else:
            return k * (5 / 2 - r + np.log(self.Nc(temperature) / concentration))

    def ettingasgausen_effect(self, temperature, concentration, activate_energy, acceptor):
        return self.alpha_t(temperature, concentration, acceptor) * self.sigma(temperature, concentration, activate_energy, acceptor) *\
               1e-2 * 0.013 / self.x(temperature, concentration, activate_energy, acceptor, 'x')


# Parameters of GaAs
class GaAs(formulas):
    name = 'GaAs'

    def __init__(self):
        self.m_dn = 0.067
        self.m_dp = 0.45
        self.epsilon = 13.1
        self.mu_n_300 = 8000
        self.mu_p_300 = 400
        self.xl = 55

    def Eg(self, temperature):
        return 1.519 - (5.405e-4/(temperature+204)) * temperature ** 2


# Parameters of Si
class Si(formulas):
    name = 'Si'

    def __init__(self):
        self.m_dn = 1.08
        self.m_dp = 0.59
        self.epsilon = 11.7
        self.mu_n_300 = 1350
        self.mu_p_300 = 450
        self.xl = 130                      # Нужно табличное значение

    def Eg(self, temperature):
        return 1.17 - 4.73e-4/(temperature + 636) * temperature ** 2


# Parameters of Ge
class Ge(formulas):
    name = 'Ge'

    def __init__(self):
        self.m_dn = 0.56
        self.m_dp = 0.37
        self.epsilon = 16.3
        self.mu_n_300 = 3900
        self.mu_p_300 = 1900
        self.xl = 58  # Нужно табличное значение

    def Eg(self, temperature):
        return 0.742 - 4.8e-4/(temperature+235) * temperature ** 2



# Class --> Object

GaAs = GaAs()
Si = Si()
Ge = Ge()

def parameters_count(temperature, material, concentration, activate_energy, acceptor):
    if material == 'GaAs': # and not 'Ge' and not 'Si':
        sc = GaAs
    elif material == 'Ge': # and not 'Si' and not 'GaAs':
        sc = Ge
    elif material == 'Si': # and not 'Ge' and not 'GaAs':
       sc = Si

    if acceptor:
        sc.type = 'p'
    else:
        sc.type = 'n'
    # Critical concentration
    n_critical = sc.n_critical(activate_energy, acceptor)

    # Points where concentration changes from n to N to ni
    def func3(temperature1_2):
        return sc.n1(temperature1_2, concentration, activate_energy, acceptor) - sc.n2(temperature1_2, concentration)
    global t_1_2
    t_1_2 = fsolve(func3, 400)[0]
    def func4(temperature_f_1_2):
        return sc.f1(temperature_f_1_2, concentration, activate_energy, acceptor) - \
               sc.f2(temperature_f_1_2, concentration, activate_energy, acceptor)
    global t_1_2_f
    t_1_2_f = fsolve(func4, 200)[0]
    Eg =  sc.Eg(temperature)
    if temperature <= t_1_2_f:
        if acceptor:
            F =  Eg/2 + sc.f1(temperature, concentration, activate_energy, acceptor)
        else:
            F =  Eg/2 - sc.f1(temperature, concentration, activate_energy, acceptor)
        n =   (sc.n1(temperature, concentration, activate_energy, acceptor))
    else:
        if acceptor:
            F =  Eg/2 + sc.f2(temperature, concentration, activate_energy, acceptor)
        else:
            F =  Eg/2 - sc.f2(temperature, concentration, activate_energy, acceptor)
        n = (sc.n2(temperature, concentration))
    lnn =  np.log(n)
    ni =  sc.ni(temperature)
    reverse_temp =  1/temperature

    Fi =  sc.fi(temperature, acceptor)
    mu =  sc.mu(temperature, concentration, acceptor)
    return round(F, 5), round(n, 5), round(lnn, 3), round(ni, 5), round(reverse_temp, 3), round(Eg, 3), round(Fi, 3), round(mu, 3)
    print("Function for count parameters")
if __name__ == '__main__':
    main()
# Change temperatures function also

# parameters('GaAs', 2e16, 0.031, 300, False)   # Валдик
# parameters('GaAs', 2e15, 0.031, 300, False)      # Кира
# parameters('Ge', 4e16, 0.011, 300, True)      # Максимилиан
# parameters('Si', 1e17, 0.045, 300, True)  # Виталик
