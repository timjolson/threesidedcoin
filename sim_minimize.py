#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 15:42:03 2018

@author: t
"""

from backend import *
import logging
from tqdm import tqdm
from scipy.optimize import minimize

logging.basicConfig(filename='./sim.log', level=logging.INFO)

#########################
start_num_flips = 500000
flips_step_rate = 50000  # increase in flips count between ratio changes
max_flips_limit = 1e9  # max number of flips for a ratio

start_timestep = 1/1000.
timestep_rate = 0.00005  # decrease in timestep between ratio changes
min_timestep_limit = 0.000001  # min timestep

goal_rate = 1/3  # rate of result == edge
tolerance = 1e-8  # tolerance to stop optimization

lims = [0.956, 0.962]  # ratio bounds from youtube video
#1. d = 2*sqrt(2) * height
#   height = d/(2*sqrt(2)) = r/sqrt(2)
#   height/r = 1/sqrt(2)
#2. d = sqrt(3) * height
#   height = d/sqrt(3) = 2r/sqrt(3)
#   height/r = 2/sqrt(3)
#########################

start_guess=0.957
# read previous results, start at best ratio
#min_loss = 1e6
#with open('results.dat', 'r') as f:
#    line = f.readline()
#    while line:
#        res = eval(line)
#        if np.fabs(res[1]) < min_loss:
#            min_loss = np.fabs(res[1])
#            start_guess = res[0]
#        line = f.readline()
#try:
#    print(f'Starting optimization with ratio: {start_guess}, loss:{min_loss}')
#except:
#    pass


sim = Sim(
    flips = start_num_flips,
    timestep = start_timestep,
)

def loss(edge, goal=goal_rate):
    logging.info(f"loss: {np.fabs(edge-goal)}")
    return np.fabs(edge - goal)

def main(ratio, sim):
    results = {'heads':0, 'tails':0, 'edge':0, 'error':0}
    assert lims[0]<=ratio<=lims[1]
    sim.ratio = ratio[0]
    logging.info(f"ratio: {sim.ratio}")
    
    for i in tqdm(range(sim.flips)):
        sim.reset_sim()
        result = sim.single_iter(
            start_orien(), start_velocity(), start_rotation(), start_position()
            )
    
        results[result] += 1
    
    edges = results['edge']/(sim.flips - results['error'])
    edges = loss(edges)
    
    with open('results.dat', 'a') as f:
        f.write(str((sim.ratio, edges, sim.flips-results['error'])) + '\n')

    logging.info(f"ratio:{ratio}, loss:{edges:.10f} results:{results}")

    sim.flips = min(sim.flips+flips_step_rate, max_flips_limit)
    sim.timestep = max(sim.timestep-timestep_rate, min_timestep_limit)

    return edges

optimize_result = minimize(main, x0=start_guess, bounds=[lims], args=(sim,), tol=tolerance)

logging.info(optimize_result)
print(optimize_result)

sim.end()

#import show_results
import mod_results
