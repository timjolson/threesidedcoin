#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 15:42:03 2018

@author: t
"""

from backend import *
from tqdm import tqdm
import logging

logging.basicConfig(filename='./sim.log', level=logging.INFO)

num_points = 200
lims = [0.955, 0.960]

sim = Sim(
    flips = 1000000,
    timestep = 1/3000.,
    sim_type = p.DIRECT,  # p.GUI, p.DIRECT, p.SHARED_MEMORY
)

def loss(edge, goal=1/3):
    logging.info(f"loss: {np.fabs(edge - goal)}")
    return np.fabs(edge - goal)

_R = list(np.linspace(lims[0], lims[1], num_points))
R = []
while _R:
    R.append(_R.pop(0))
    try:
        R.append(_R.pop(-1))
    except IndexError:
        pass

logging.info(f'Starting sim of {num_points} points, {sim.flips} flips each, in range {lims}.')

for r in tqdm(R, position=0):
    results = {'heads':0, 'tails':0, 'edge':0, 'error':0}
    sim.ratio = r
    logging.info(f"ratio: {sim.ratio}")
    
    for i in tqdm(range(sim.flips)):
        sim.reset_sim()
        result = sim.single_iter(
            start_orien(), start_velocity(), start_rotation(), start_position()
            )
    
        results[result] += 1

    logging.info(results)
    
    edges = results['edge']/(sim.flips - results['error'])
    edges = loss(edges)
    
    with open('results.dat', 'a') as f:
        f.write(str((sim.ratio, edges, sim.flips-results['error'])) + '\n')

sim.end()

logging.info('Finished linspace sim.')
print('done')

import plot_results
