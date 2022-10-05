# my test
from enum import EnumMeta
from logging import root
import pybamm
import numpy as np
import matplotlib.pyplot as plt
import os 
import sys
sys.path.append("..")
sys.path.extend([os.path.join(root, name) for root, dirs, _ in os.walk("../") for name in dirs])

from tec_reduced_model.set_parameters import set_thermal_parameters
from tec_reduced_model.set_parameters import (
    set_thermal_parameters,
    set_experiment_parameters,
    set_ambient_temperature,
)
from tec_reduced_model.process_experimental_data import import_thermal_data, get_idxs
from scipy.interpolate import interp1d

pybamm.set_logging_level("INFO")

def plot_model_solutions(axes, solution, Crate, temperature):
    if solution.model.name == "TSPMe":
        ls = "-"
        color = "black"
        linewidth = 0.75
    else:
        ls = ":"
        color = "gray"
        linewidth = 1

    axes[0].plot(
        solution["Time [s]"].entries,
        solution["Terminal voltage [V]"].entries,
        color=color,
        label=solution.model.name,
        ls=ls,
        linewidth=linewidth,
    )

    if solution.model.name == "TSPMe":
        axes[0].scatter(
            0,
            solution["X-averaged battery open circuit voltage [V]"].entries[0],
            s=15,
            marker="x",
            color="black",
            linewidths=0.75,
        )

    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("Voltage (V)")

    axes[1].plot(
        solution["Time [s]"].entries,
        solution["X-averaged cell temperature [K]"].entries - 273.15,
        color=color,
        label=solution.model.name,
        ls=ls,
        linewidth=linewidth,
    )

    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Cell temperature (°C)")
    axes[1].legend()

    if temperature == 25 and Crate == 1:
        axes[1].set_yticks([25, 28, 31, 34, 37])

    return axes

def compare_data(models,param,Crate,temperature):
    fig,axes=plt.subplots(3,2,figsize=(5.7,5.5))
    for k,Crate in enumerate(Crates):
        param = set_experiment_parameters(param, Crate, temperature)
        param = set_ambient_temperature(param, Crate, temperature)
        expriment=pybamm.Experiment(
            [(f"Discharge at {Crate}C until 2.5 V (5 seconds period)","Rest for 2 hours")],
            period="30 seconds"
            
        )
        solutions=[]
        for model in models:
            simulation=pybamm.Simulation(
                model,
                parameter_values=param,
                experiment=expriment
            )
            solution=simulation.solve()
            solutions.append(solution)

models=[
    pybamm.lithium_ion.DFN(
        options={
            "thermal":"lumped",
            "cell geometry": "arbitrary",
        },
        name="TDFN"
    ),
    # pybamm.lithium_ion.SPMe(
    #     options={
    #         "thermal":"lumped",
    #         "cell geometry": "arbitrary",
    #         "electrolyte conductivity":"integrated",
    #     },
    #     name="TSPMe"
    # )
    pybamm.lithium_ion.DFN(
        options={
            "thermal":"lumped"
        },
        name="TSPMe"
    )
]

param=pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)
temperatures=[0,10,25]
Crates=[0.5,1,2]
root=os.path.dirname(os.path.dirname(__file__))

for temperature in temperatures:
    param=set_thermal_parameters(param,16,2.32e6,temperature)
    compare_data(models,param,Crates,temperature)