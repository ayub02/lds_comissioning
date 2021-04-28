import numpy as np
import sys
sys.path.insert(1, '../code/')
from vcf_calc import VCFOperational_Pressure as VCF


def reynold_num(dia, vel, kin_visc):
    return vel * dia / kin_visc


def darcy(_dia, _eta, _vel, _kin_visc):
    Re = reynold_num(_dia, _vel, _kin_visc)
    fd = 0.011
    for i in range(10):
        a = 2 * np.log10(_eta / 3.7 / _dia + 2.51 / Re / np.sqrt(fd))
        fd = (1 / a) ** 2
    return fd


def op_density(_norm_density, pressure, temp):
    op_density_list = np.linspace(_norm_density - 20, _norm_density + 20, 50, endpoint=True)
    norm_density_list = []
    for val in op_density_list:
        norm_density_list.append(val / VCF(val, pressure, temp))
    return np.interp(_norm_density, norm_density_list, op_density_list)


eta = 15e-5
norm_density = 830
kin_viscosity = 0.000002
dia = (457.2-6.4*2)/1000
area = 3.14*dia**2/4
noLeakFlow = 683.624
vel = noLeakFlow/3600/area
pressure_KBS = 65e5
prod_temp_KBS = 20
norm_density = 828.011
oper_density_KBS = op_density(norm_density, pressure_KBS/1e5, prod_temp_KBS)
fD = darcy(dia, eta, vel, kin_viscosity)
gradient = fD*oper_density_KBS*vel**2/2/dia
print(gradient)