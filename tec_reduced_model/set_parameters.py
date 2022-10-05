#
# Definitions for the tuned parameters to the experiment
#

import pybamm
import numpy as np
from tec_reduced_model.process_experimental_data import import_thermal_data, get_idxs

'''
根据设定的值和默认值之间的倍数关系，调整某些参数的值
'''
def set_thermal_parameters(param, h, cp, T):
    cp_factor = cp / param.evaluate(pybamm.ThermalParameters().rho_eff_dim(T))
    h_factor = h / param.evaluate(pybamm.ThermalParameters().h_total_dim)

    param["Total heat transfer coefficient [W.m-2.K-1]"] *= h_factor
    param["Positive current collector specific heat capacity [J.kg-1.K-1]"] *= cp_factor
    param["Negative current collector specific heat capacity [J.kg-1.K-1]"] *= cp_factor
    param["Negative electrode specific heat capacity [J.kg-1.K-1]"] *= cp_factor
    param["Separator specific heat capacity [J.kg-1.K-1]"] *= cp_factor
    param["Positive electrode specific heat capacity [J.kg-1.K-1]"] *= cp_factor

    return param

'''
有效扩散系数和粒子浓度受温度影响很大，需要根据经验进行调整
'''
def set_experiment_parameters(param, Crate, T):
    if T == 25:
        cp0 = 17150
        if Crate == 0.5:
            Dn = 0.9e-14
        elif Crate == 1:
            Dn = 2e-14
        elif Crate == 2:
            Dn = 6e-14
    elif T == 10:
        cp0 = 17750
        if Crate == 0.5:
            Dn = 0.4e-14
        elif Crate == 1:
            Dn = 1e-14
        elif Crate == 2:
            Dn = 3e-14
    elif T == 0:
        cp0 = 18150
        if Crate == 0.5:
            Dn = 0.22e-14
        elif Crate == 1:
            Dn = 0.55e-14
        elif Crate == 2:
            Dn = 1.5e-14

    param["Negative electrode diffusivity [m2.s-1]"] = Dn
    param["Initial concentration in positive electrode [mol.m-3]"] = cp0

    return param

'''
根据当前温度调整参数
'''
def set_ambient_temperature(param, Crate, T):
    dataset = import_thermal_data(Crate, T)
    T_end = []
    for _, data in dataset.items():
        idx_end = get_idxs(data, Crate * 5, 5 / 3)[1]
        if len(idx_end) > 1:
            T_end.append(data["Temp Cell [degC]"][idx_end[1]])

    real_temperature = np.mean(T_end)
    param["Ambient temperature [K]"] = 273.15 + real_temperature
    param["Initial temperature [K]"] = 273.15 + real_temperature

    return param
