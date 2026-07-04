from __future__ import division, print_function

from Numerical_solution import Dynamics_Solver
import os
from numpy import array
try:
    xrange
except NameError:
    xrange = range
w_min=0.05
w_max=6.0
name = "Calc_file_gpaw/CH4_simulation.gpw"
sim_material = Dynamics_Solver(name,minw=w_min,maxw=w_max)
resonance, omegas, T_mount = sim_material.range_omega()
# the program is designed for emulated in 4 nodes if you wish changed you will change the following number

n_nodes=int(os.environ.get('SLURM_ARRAY_TASK_COUNT', '4'))
number_of_node=int(os.environ.get('SLURM_ARRAY_TASK_ID', '0'))
local_omegas=array([omegas[i] for i in xrange(len(omegas)) if i % n_nodes == number_of_node])
if resonance:
    print("This system has resonance in the range of {} to {} eV".format(sim_material.minw, sim_material.maxw))
else:
    print("This system has no resonance in the range of {} to {} eV".format(sim_material.minw, sim_material.maxw))

for ome in local_omegas:
    sim_material.simulate_c_dt(ome, T_mount)

del sim_material






