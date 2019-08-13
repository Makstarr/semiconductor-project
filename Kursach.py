# Вычисление параметров полупроводниковых материалов
# Построение температурных зависимостей
# Tarasov MD


import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.optimize import fsolve


# Constants
q = 1.6e-19
kb = 1.38e-23
k = 1.38e-23 / q  # Ev
N_avagadro = 6e23
v_snd = 343
h = 43.903876e-68
pi = math.pi
me = 9.11e-31


# Semiconductors parameters that independent from material
class Semiconductor:
    def temperature_1 (self, concentration, activate_energy, acceptor):
        # Temperature of impurity ionisation
        def func(temperature):
            return concentration / 1.98e15 / temperature ** 1.5 * np.exp(activate_energy / k / temperature) - 3

        ionization_temperature = fsolve(func, 50)
        return ionization_temperature[0]

    def temperature_2(self, concentration, activate_energy, acceptor):
        # Temperature of intrinsic carriers  ionisation
        def func2(temperature_2):
            return self.ni(temperature_2) - concentration * np.sqrt(2)
        self_conduction_temperature = fsolve(func2, 550)
        return  self_conduction_temperature[0]

    def Nv(self, temperature):
        return (2 * ((2 * self.m_dp * pi * me * kb * temperature) / h) ** 1.5) / 1000000

    def Nc(self, temperature):
        return (2 * ((2 * self.m_dn * pi * me * kb * temperature) / h) ** 1.5) / 1000000

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
            return self.Nc(temperature) / 4 * np.exp(-1 * activate_energy / (k * temperature)) * \
                   (np.sqrt(
                       1 + 8 * concentration / self.Nc(temperature) * np.exp(activate_energy / k / temperature)) - 1)

    def n2(self, temperature, concentration):
        return (concentration / 2) * (1 + np.sqrt(1 + 4 * self.ni(temperature) ** 2 / concentration ** 2))

    def fi(self, temperature, acceptor):
        if acceptor:
            return k * temperature * np.log((self.m_dp / self.m_dn) ** (3 / 4))
        else:
            print('FI ----- ХЗХЫЧ НЕ УВЕРЕН ЧТО ТАКАЯ ФОРМУЛА МОЖЕТ МАССЫ НАОБОРОТ')
            return k * temperature * np.log((self.m_dn / self.m_dp) ** (3 / 4))

    def f1(self, temperature, concentration, activate_energy, acceptor):
        if acceptor:
            return -self.Eg(temperature) / 2 + k * temperature * np.log(self.Nv(temperature) / (
                        (self.Nv(temperature) * np.exp(-activate_energy / (k * temperature)) / 2) * (-1 + np.sqrt(
                    1 + 8 * (concentration / self.Nc(temperature)) * np.exp(activate_energy / (k * temperature))))))
        else:
            # не доделал
            return 0

    def f2(self, temperature, concentration, activate_energy, acceptor):
        if acceptor:
            return -self.Eg(temperature) / 2 + k * temperature * np.log(self.Nv(temperature) / (concentration / 2 * (1 + np.sqrt(1 + 4 * (self.ni(temperature) ** 2) / (concentration ** 2)))))
        else:
            # не доделал
            return 0

    def t_min_fermi(self, concentration, acceptor):
        if acceptor:
            return 8.15 * (1 / self.m_dp) * (concentration / 1e18) ** (2 / 3)
        else:
            return 8.15 * (1 / self.m_dn) * (concentration / 1e18) ** (2 / 3)

    def fermi_min(self, concentration, activate_energy, acceptor):
        if acceptor:
            return (self.Eg(self.t_min_fermi(concentration, acceptor)) / 2 -
                    ((self.Eg(self.t_min_fermi(concentration, acceptor)) / 2)
                    - activate_energy)) / 2 - 5.3e-4 * (1 / self.m_dp) * (concentration / 1e18) ** (2 / 3)
        else:
            return (self.Eg(self.t_min_fermi(concentration, acceptor)) / 2 -
                    ((self.Eg(self.t_min_fermi(concentration, acceptor)) / 2)
                    - activate_energy)) / 2 - 5.3e-4 * (1 / self.m_dn) * (concentration / 1e18) ** (2 / 3)

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
        if acceptor:
            return q*concentration*self.mu_p_300
        else:
            return q * concentration * self.mu_n_300


    # ПОКА НЕ РАЗОБРАЛИСЬ
    def x(self, temperature, concentration, acceptor, x):
        # Не доделано
        if acceptor:
            xl = 60
            # xl =(1 / 3) * (3 * kb * N_avagadro) * v_snd * (10 * 5.55e-10) ????????
            xe = 2 * (kb ** 2) * temperature / q * concentration * 1e6 * self.mu(temperature, concentration, acceptor) / 1e4
        if x =='x':
            return xl + xe
        elif x == 'xl':
            return xl
        else:
            return xe

    # Не доделан
    def Rh(self, temperature, concentration, acceptor):
        if True:
            r = 1.18
            return r / q / concentration / 1e6
        else:
            r = 1.93
            return r / q / concentration / 1e6

    # Не доделан
    def alpha_t(self,temperature, concentration, acceptor):
        if True:
            r =1/2
        else:
            r = '????'
        if acceptor:
            return k * (5 / 2 - r + np.log(self.Nv(temperature) / concentration))
        else:
            return k * (5 / 2 - r + np.log(self.Nc(temperature) / concentration))

    # Не доделан
    def ettingasgausen_effect(self, temperature, concentration, activate_energy, acceptor):
        return self.alpha_t(temperature, concentration, acceptor) * self.sigma(temperature, concentration, activate_energy, acceptor) *\
               1e-2 * 0.013 / self.x(temperature, concentration, acceptor, 'x')


# Parameters of Germanium
class Ge(Semiconductor):
    name = 'Germanium'

    def __init__(self):
        self.m_dn = 0.56
        self.m_dp = 0.34
        self.epsilon = 16.3
        self.mu_n_300 = 3900
        self.mu_p_300 = 1900

    def Eg(self, temperature):
        return 0.742 - (4.8e-4 / (temperature + 235)) * temperature ** 2


# Graph with temperature dependence of Fermi level
class GraphWithFermi:
    Ec = []
    Ev = []
    Eg = []
    Ei = []
    Fi = []
    F = []
    Ea = []
    temp = []

    def count_and_draw(self, concentration, activate_energy, acceptor, sc, start, end):
        fermi_txt = open(sc.name + sc.type + ' fermi.txt', 'w')
        fermi_i_txt = open(sc.name + sc.type + ' fermi_i_txt', 'w')
        Egap_txt = open(sc.name + sc.type + ' Egap.txt', 'w')
        for temperature in range(start, end):
            self.temp.append(temperature)
            self.Eg.append(sc.Eg(temperature))
            self.Ei.append(0)
            self.Ec.append(sc.Eg(temperature) / 2)
            self.Ev.append(- sc.Eg(temperature) / 2)
            self.Ea.append(- sc.Eg(temperature) / 2 + activate_energy)
            self.Fi.append(sc.fi(temperature, acceptor))
            if temperature <= t_f_1_2:
                self.F.append(sc.f1(temperature, concentration, activate_energy, acceptor))
            else:
                self.F.append(sc.f2(temperature, concentration, activate_energy, acceptor))

            # Не доделал там Егэп +- в зависимости от типа
            if temperature % 5 == 0 and temperature <= t_1_2 and acceptor:
                Egap_txt.write(str(sc.Eg(temperature)) + '\n')
                fermi_i_txt.write(str(sc.fi(temperature, acceptor))+ '\n')
                fermi_txt.write(str(sc.Eg(temperature) / 2 + sc.f1(temperature, concentration, activate_energy, acceptor)) + '\n')
            elif temperature % 5 == 0 and temperature > t_1_2 and acceptor:
                Egap_txt.write(str(sc.Eg(temperature)) + '\n')
                fermi_i_txt.write(str(sc.fi(temperature, acceptor)) + '\n')
                fermi_txt.write(str(sc.Eg(temperature) / 2 + sc.f2(temperature, concentration, activate_energy, acceptor)) + '\n')
        fermi_txt.close()
        fermi_i_txt.close()
        Egap_txt.close()
        plt.figure(sc.name + sc.type + ' fermi level')
        plt.title('Температурная зависимость уровня Ферми')
        plt.xlabel('Температра Т, К')
        plt.ylabel('Энергия Е, эВ')
        plt.plot(self.temp, self.Ea, 'g-', label='Ea', linewidth=1)
        plt.plot(self.temp, self.Ec, label='Ec', linewidth=1)
        plt.plot(self.temp, self.Ev, 'b-', label='Ev', linewidth=1)
        plt.plot(self.temp, self.Ei, 'k--', label='Ei', linewidth=1)
        plt.plot(self.temp, self.Fi, 'y--', label='Fi', linewidth=1)
        plt.plot(self.temp, self.F, 'r-', label='F', linewidth=1)
        plt.legend()
        plt.show()


# Graph with temperature dependence of concentration ln(n)(1/T)
class GraphWithConcentration:
    T1 = []
    T2 = []
    ln_n = []
    reverse_temp = []

    def count_and_draw(self, concentration, activate_energy, acceptor, sc, start, end):
        concentration_txt = open(sc.name + sc.type + ' concentration.txt', 'w')
        concentration_i_txt = open(sc.name + sc.type + ' concentration_i.txt', 'w')
        t1 = sc.temperature_1(concentration, activate_energy, acceptor)
        print("T1 = %.2f " % t1)
        t2 = sc.temperature_2(concentration, activate_energy, acceptor)
        print("T2 = %.2f " % t2)
        for temperature in range(start, end):
            self.reverse_temp.append(1 / temperature)
            self.T1.append(1 / t1)
            self.T2.append(1 / t2)
            n1 = sc.n1(temperature, concentration, activate_energy, acceptor)
            n2 = sc.n2(temperature, concentration)
            # НА СТРОКЕ ±323 ОБЬЯСНЕНИЕ t_1_2
            if temperature <= t_1_2:
                if temperature % 5 == 0:
                    concentration_txt.write(str(n1) + '\n')
                    concentration_i_txt.write(str(sc.ni(temperature)) + '\n')
                self.ln_n.append(np.log(n1))
            else:
                if temperature % 5 == 0:
                    concentration_txt.write(str(n2) + '\n')
                    concentration_i_txt.write(str(sc.ni(temperature)) + '\n')
                self.ln_n.append(np.log(n2))
        concentration_txt.close();
        plt.figure(sc.name + sc.type + ' concentration')
        plt.title('Температурная зависимость концентрации носителей ' + sc.name)
        plt.xlabel('1/T, 1/K')
        y_label = 'ln(' + sc.type + ')'
        plt.ylabel(y_label)
        plt.plot(self.reverse_temp, self.ln_n, color='CadetBlue', label=y_label, linewidth=2)
        plt.plot(self.T1, self.ln_n, color='black', label=("%.2f" % t1), linewidth=1)
        plt.plot(self.T2, self.ln_n, color='black', label=("%.2f" % t2), linewidth=1)
        plt.legend()
        plt.show()


# Graph with temperature dependence of mobility
class GraphWithMobility:
    temp = []
    mobility = []

    def count_and_draw(self, concentration, activate_energy, acceptor, sc, start, end):
        mobility_txt = open(sc.name + sc.type + ' mobility.txt', 'w')
        for temperature in range(start, end):
            self.temp.append(temperature)
            mu = sc.mu(temperature, concentration, acceptor)
            self.mobility.append(mu)
            if temperature % 5 == 0:
                mobility_txt.write(str(mu) + '\n')
        mobility_txt.close();
        plt.figure(sc.name + sc.type + ' mobility (µ)')
        plt.title('Температурная зависимость подвижности')
        plt.xlabel('Температура Т, К')
        plt.ylabel('Подвижность µ, см^2/В с ')
        plt.plot(self.temp, self.mobility, 'g-', label='µ', linewidth=1)
        plt.legend()
        plt.show()


# Class --> Object
Ge = Ge()
graph_with_concentration: GraphWithConcentration = GraphWithConcentration()
graph_with_fermi: GraphWithFermi = GraphWithFermi()
graph_with_mobility: GraphWithMobility = GraphWithMobility()


# Function that drawing plots
def plots(material, concentration, activate_energy, acceptor):
    if material == 'Ge' or 'ge' or 'germanium' or 'Германий':
        sc = Ge
    if acceptor:
        sc.type = 'p'
    else:
        sc.type = 'n'
    # Critical concentration
    n_critical = sc.n_critical(activate_energy, acceptor)
    print("N крит = %.2f" % n_critical)

    # Я НЕ ЗНАЮ ПОЧЕМУ n1 ВСЕГДА МЕНЬШЕ Na
    # (n2 = NA ДО ПЕРЕХОДА В i ОБЛАСТЬ)
    # ПОЭТОМУ ТУПА СОЕДИНЯЮ ГРАФИК В ТОЧКЕ ПОЧТИ ПЕРЕСЕЧЕНИЯ n1 И n2 (ОНИ ВООБЩЕ НЕ ПЕРЕСЕКАЮТСЯ)
    def func3(temperature1_2):
        return sc.n1(temperature1_2, concentration, activate_energy, acceptor) - sc.n2(temperature1_2, concentration)

    global t_1_2
    t_1_2 = fsolve(func3, 400)[0]

    def func4(temperaturef1_2):
        return sc.f1(temperaturef1_2, concentration, activate_energy, acceptor) - sc.f2(temperaturef1_2, concentration, activate_energy, acceptor)
    global t_f_1_2
    t_f_1_2 = fsolve(func4, 10)[0]
    # t_f_1_2 - ТОЧКА ПОЧТИ ПЕРЕСЕЧЕНИЯ ГРАФИКОВ ферми

    # Graphics
    graph_with_concentration.count_and_draw(concentration, activate_energy, acceptor, sc, 5, 1002)
    graph_with_fermi.count_and_draw(concentration, activate_energy, acceptor, sc, 10, 1002)
    graph_with_mobility.count_and_draw(concentration, activate_energy, acceptor, sc, 5, 1002)


# Function that counts parameters at given temperature
def parameters(material, concentration, activate_energy, temperature, acceptor):
    if material == 'Ge' or 'ge' or 'germanium' or 'Германий':
        sc = Ge
    if acceptor:
        sc.type = 'p'
    else:
        sc.type = 'n'
    t1 = sc.temperature_1(concentration, activate_energy, acceptor)
    print("T1 = %.2f " % t1)
    t2 = sc.temperature_2(concentration, activate_energy, acceptor)
    print("T2 = %.2f " % t2)
    print('T(F min) = ' + str(sc.t_min_fermi(concentration, acceptor)))
    print('F min = ' + str(sc.fermi_min(concentration, activate_energy, acceptor)))
    mu = sc.mu(temperature, concentration, acceptor)
    sigma = sc.sigma(temperature, concentration, activate_energy, acceptor)
    rh = sc.Rh(temperature, concentration, acceptor)
    xe = sc.x(temperature, concentration, acceptor, 'xl')
    xl = sc.x(temperature, concentration, acceptor, 'xe')
    x = sc.x(temperature, concentration, acceptor, 'x')
    alpha_t = sc.alpha_t(temperature, concentration, acceptor)
    ettingasgausen = sc.ettingasgausen_effect(temperature, concentration, activate_energy, acceptor)
    parameters_txt = open(sc.name + sc.type+" parameters.txt", "w")
    parameters_txt.write('µ(' + str(temperature) + ')=' + str(mu) + ' cm^2/B*c' + '\n')
    parameters_txt.write('сигма(' + str(temperature) + ')=' + str(sigma) + ' Ом*сm' + '\n')
    parameters_txt.write('R(' + str(temperature) + ')=' + str(rh) + ' m^3/Кл' + '\n')
    parameters_txt.write('xl(' + str(temperature) + ')=' + str(xl) + ' Вт/m*K' + '\n')
    parameters_txt.write('xe(' + str(temperature) + ')=' + str(xe) + ' Вт/m*K' + '\n')
    parameters_txt.write('x(' + str(temperature) + ')=' + str(x) + ' Вт/m*K' + '\n')
    parameters_txt.write('alpha(' + str(temperature) + ')=' + str(alpha_t) + ' В/K' + '\n')
    parameters_txt.write('Ue/Uh(' + str(temperature) + ')=' + str(ettingasgausen) + '\n')
    parameters_txt.close()


# Change temperatures function also
parameters('Ge', 4e16, 0.011, 300, True)
plots('Ge', 4e16, 0.011, True)
