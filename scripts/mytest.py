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

def plot_experimental_data(axes, Crate, temperature, cells_ignore):
    dataset = import_thermal_data(Crate, temperature)
    data_conc = {"time": [], "voltage": [], "temperature": []}

    for cell, data in dataset.items():
        if cell in cells_ignore:
            continue

        idx_start, idx_end = get_idxs(data, Crate * 5, 5 / 3)
        if len(idx_end) == 1:
            idx_end = np.append(idx_end, len(data["Time [s]"]))
        axes[0].plot(
            data["Time [s]"][idx_start[0] : idx_end[1]]
            - data["Time [s]"][idx_start[0]],
            data["Voltage [V]"][idx_start[0] : idx_end[1]],
            label=cell,
            linewidth=1,
            ls="--",
        )
        axes[1].plot(
            data["Time [s]"][idx_start[0] : idx_end[1]]
            - data["Time [s]"][idx_start[0]],
            data["Temp Cell [degC]"][idx_start[0] : idx_end[1]],
            label=cell,
            linewidth=1,
            ls="--",
        )
        pad = 4

        axes[0].annotate(
            "{}C".format(Crate),
            xy=(0, 0.5),
            xytext=(-axes[0].yaxis.labelpad - pad, 0),
            xycoords=axes[0].yaxis.label,
            textcoords="offset points",
            size="large",
            ha="right",
            va="center",
        )

        data_conc["time"] = np.append(
            data_conc["time"],
            data["Time [s]"][idx_start[0] : idx_end[1]]
            - data["Time [s]"][idx_start[0]],
        )
        data_conc["voltage"] = np.append(
            data_conc["voltage"], data["Voltage [V]"][idx_start[0] : idx_end[1]]
        )
        data_conc["temperature"] = np.append(
            data_conc["temperature"],
            data["Temp Cell [degC]"][idx_start[0] : idx_end[1]],
        )

    return axes, data_conc

def plot_model_solutions(axes, solution, Crate, temperature):
    if solution.all_models[0].name == "TDFN":
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
        label=solution.all_models[0].name,
        ls=ls,
        linewidth=linewidth,
    )

    if solution.all_models[0].name == "TDFN":
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
        label=solution.all_models[0].name,
        ls=ls,
        linewidth=linewidth,
    )

    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Cell temperature (°C)")
    axes[1].legend()

    if temperature == 25 and Crate == 1:
        axes[1].set_yticks([25, 28, 31, 34, 37])

    return axes

def compare_data(models,param,Crate,temperature,cells_ignore=None):
    fig,axes=plt.subplots(3,2,figsize=(10,15))
    for k,Crate in enumerate(Crates):
        param = set_experiment_parameters(param, Crate, temperature)
        param = set_ambient_temperature(param, Crate, temperature)
        expriment=pybamm.Experiment(
            [(f"Discharge at {Crate}C until 2.5 V (5 seconds period)","Rest for 2 hours")],
            period="30 seconds"
            
        )
        solutions=[]

        axes[k,:],data_conc=plot_experimental_data(
            axes[k,:],Crate,temperature,cells_ignore
        )

        for model in models:
            simulation=pybamm.Simulation(
                model,
                parameter_values=param,
                experiment=expriment
            )
            solution=simulation.solve()
            solutions.append(solution)
            axes[k,:]=plot_model_solutions(axes[k,:],solution,Crate,temperature)
        
        fig.suptitle(f"Ambient temperature: {temperature} °C")
        fig.tight_layout()
        fig.subplots_adjust(left=0.15, top=0.92)
    return fig

models=[
    pybamm.lithium_ion.DFN(
        options={
            "thermal":"lumped",
            "cell geometry": "arbitrary",
        },
        name="TDFN_arbitrary"
    ),
    pybamm.lithium_ion.SPMe(
        options={
            "thermal":"lumped",
        },
        name="TDFN"
    )
]

param=pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)
temperatures=[0,10,25]
Crates=[0.5,1,2]
cells_ignore = ["791"]
root=os.path.dirname(os.path.dirname(__file__))

for temperature in temperatures:
    param=set_thermal_parameters(param,16,2.32e6,temperature)
    fig=compare_data(models,param,Crates,temperature,cells_ignore=cells_ignore)
    # plt.show()
    fig.savefig(
        os.path.join(root, "figures", "mytest2_{}degC.png".format(temperature)),
    )