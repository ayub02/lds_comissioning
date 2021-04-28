import sys, os
sys.path.append('../code/')
from vcf_calc import VCFOperational_Pressure as VCF
import numpy as np


def op_density(_norm_density, pressure, temp):
    op_density_list = np.linspace(_norm_density - 20, _norm_density + 20, 50, endpoint=True)
    norm_density_list = []
    for val in op_density_list:
        norm_density_list.append(val / VCF(val, pressure, temp))
    return np.interp(_norm_density, norm_density_list, op_density_list)

print(op_density(830, 65, 20))
print(op_density(830, 1, 20))