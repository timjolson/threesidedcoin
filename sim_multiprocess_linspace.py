#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 15:42:03 2018

@author: t
"""

from backend import *
from tqdm import tqdm
from scipy.optimize import minimize
import logging, multiprocessing
from copy import copy

CPU_COUNT = multiprocessing.cpu_count()

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler('./sim.log')
fh.setLevel(logging.INFO)
logger.addHandler(fh)

num_points = 250
flips = 3000
timestep = 1/2000.
lims = [0.85, 1.0]

def loss(edge, goal=1/3):
    return np.fabs(edge - goal)

#R = multiprocessing.Queue()
#for r in np.linspace(lims[0], lims[1], num_points):
#    R.push(r)
R = list(np.linspace(lims[0], lims[1], num_points))

logger.info(f'Starting sim of {num_points} points, {flips} flips each, in range {lims}.')

def main(ratio):
    sim=Sim(flips=flips, ratio=ratio, timestep=timestep, sim_type=p.DIRECT)
    results = {'heads':0, 'tails':0, 'edge':0, 'error':0}
    
    for i in range(sim.flips):
        sim.reset_sim()
        result = sim.single_iter(
            start_orien(), start_velocity(), start_rotation(), start_position()
            )

        results[result] += 1

    logger.debug(results)
    
    edges = results['edge']/(sim.flips - results['error'])
    edges = loss(edges)
    
    with open('results.dat', 'a') as f:
        f.write(str((ratio, edges, sim.flips-results['error'])) + '\n')

    return (ratio, edges, sim.flips-results['error'])
    
pool = multiprocessing.Pool()
res = pool.imap_unordered(main, R)
pool.close()
pool.join()

#multiprocessing.Process(target=main, args=(R, res, sim)).start()

logging.info('Finished linspace sim.')
print('done')

import show_results
