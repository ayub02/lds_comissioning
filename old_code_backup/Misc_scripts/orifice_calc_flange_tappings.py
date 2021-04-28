import numpy as np
from matplotlib import pyplot as plt


# Pipe properties
OD = 60.33/1000                             # m NPS 2"
Wall_thickness = 3.912/1000                 # m NPS 2" SCH-40
ID = OD-2*Wall_thickness                    # m
Area = 3.14*ID**2/4                         # m2
DS = OD                                     # m Plate support diameter (assumed outer diameter of ANSI B16.5 Class 600 flange for 2-1/2" NPS pipe)

# Orifice properties
d = 19/1000                               # m Orifice diameter (12.5mm and 19mm viable options)
e = 0.02*ID                                 # m Thickness of orifice
E = 3.2/1000                                # m Thickness of plate
El = 193e9                                  # Pa Modulus of elasticity of SS304 or 316
Yeild = 215e6                               # Pa Yeild stress as per ISO TR 9464
beta = d/ID                                 # - Ratio

# Fluid properties
kin_visc = 0.000002                         # m2/s
rho = 830                                   # kg/m3
Exp = 1                                     # Expansion coefficient for liquids

# Process conditions
Flow = 0.02*500/3600                       # m3/s
qm = Flow*rho                               # kg/s
vel = Flow/Area                             # m/s
ReD = vel*ID/kin_visc                       # - Reynolds number

# For flange
L1 = 25.4/ID/1000
L2 = 25.4/ID/1000

assert ID >= 50/1000, "ID is less than 50 mm"
assert ID <= 1, "ID is greater than 1000 mm"
assert e >= 0.005*ID, "Orifice thickness is less than 0.005D"
assert e <= 0.02*ID, "Orifice thickness is greater than 0.02D"
assert E >= e, "E is less than e"
if 50/1000 <= ID <= 64/1000:
    assert E <= 3.2/1000, "E is greater than 3.2 mm"
else:
    assert E <= 0.05*ID, "E is greater than 0.05D"

assert d >= 12.5/1000, "d is less than 12.5 mm"
assert beta >= 0.1, "beta is less than 0.1"
assert beta <= 0.75, "beta is greater than 0.75"
assert ReD >= 5000
assert ReD >= 170*beta**2*(ID*1000)


# Flow coefficient calculation
M2 = 2*L2/(1-beta)
A = (19000*beta/ReD)**0.8
C = 0.5961 + 0.0261*beta**2 - 0.216*beta**8 + 0.000521*(1e6*beta/ReD)**0.7 + (0.0188 + 0.0063*A)*beta**3.5*(1e6/ReD)**0.3 + \
    (0.043 + 0.08*np.exp(-10*L1) - 0.123*np.exp(-7*L1))*(1-0.11*A)*(beta**4/(1-beta**4)) - 0.031*(M2 - 0.8*M2**1.1)*beta**1.3 + \
    0.011*(0.75-beta)*(2.8-ID*1000/25.4)

# Pressure drop between -L1 and +L2 locations
dP = (qm*(1-beta**4)**0.5*4/C/Exp/3.14/d**2)**2/2/rho

# Overall pressure drop of orifice plate
var = ((1 - beta**4 * (1 - C**2))**0.5 - C*beta**2) / ((1 - beta**4 * (1 - C**2))**0.5 + C*beta**2)
dP_overall = var*dP

print('-'*60)
print('\t\t\t\t\t Pipe properties')
print('-'*60)
print("Pipe OD \t\t\t\t", round(OD*1000, 2), '\t\t mm')
print("Pipe thickness \t\t\t", round(Wall_thickness*1000, 2), '\t\t mm')
print("Pipe ID \t\t\t\t", round(ID*1000, 2), '\t\t mm')
print("Cross-section area \t\t", round(Area*1e6, 2), '\t mm2')

print('-'*60)
print('\t\t\t\t\t Orifice properties')
print('-'*60)
print("Orifice diameter \t\t", round(d*1000, 2), '\t\t mm')
print("Orifice thickness \t\t", round(e*1000, 2), '\t\t mm')
print("Plate thickness \t\t", round(E*1000, 2), '\t\t mm')
print("E/DS \t\t\t\t\t", round(E/DS, 3), '\t\t mm')
print("beta \t\t\t\t\t", round(beta, 2), '\t\t --')

print('-'*60)
print('\t\t\t\t\t Fluid properties')
print('-'*60)
print("Density \t\t\t\t", round(rho, 2), '\t\t kg/m3')
print("Kinematic viscosity \t", round(kin_visc*1e6, 2), '\t\t cSt')

print('-'*60)
print('\t\t\t\t\t Process conditions')
print('-'*60)
print("Vol flow rate \t\t\t", round(Flow*3600, 1), '\t\t m3/hr \t\t', round(Flow*1000, 1), '\t\t liter/s')
print("Flow vel upstream \t\t", round(vel, 1), '\t\t m/s')
print("Mass flow rate \t\t\t", round(qm, 1), '\t\t kg/s')
print("Reynolds \t\t\t\t", round(ReD), '\t\t --')

print('-'*60)
print('\t\t\t\t\t Calculations')
print('-'*60)
print("Flow coefficient \t\t", round(C, 3), '\t\t --')
print("Pressure drop orifice \t", round(dP/1e5, 4), '\t bar \t\t\t', round(dP/1000, 1), '\t\t kPa')
print("Pressure drop overall \t", round(dP_overall/1e5, 4), '\t bar \t\t\t', round(dP_overall/1000, 1), '\t\t kPa')

a = beta * (13.5 - 15.5 * beta)
b = 117 - 106 * beta ** 1.3
stress_measure_1 = abs(-dP / El * (DS/E) ** 2 * (a * DS/E - b))
stress_measure_2 = (dP/Yeild*(0.681-0.651*beta))**0.5

print("100dqm/qm < 0.1 \t\t", round(stress_measure_1, 3), '\t\t --')
print("E/DS >  \t\t\t\t", round(stress_measure_2, 3), '\t\t --')

assert stress_measure_1 <= 0.1, "100 dqm/qm is greater than 0.1"
assert E/DS > stress_measure_2, "E/DS is less than required by yield strength"


