#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 15:42:03 2018

@author: t
"""

from simulator import *
import logging
from tqdm import tqdm
import os
from scipy.optimize import minimize

logging.basicConfig(filename='./sim.log', filemode='w', level=logging.INFO, format="%(filename)s:%(funcName)s:%(lineno)s:%(msg)s")

#########################
start_num_flips = 1_000_000
flips_step_rate = 200_000  # increase in flip count between ratio changes
max_flips_limit = 1e7  # max number of flips for any ratio

start_timestep = 1/1500.
timestep_rate = 1/20000  # decrease in timestep between ratio changes
min_timestep_limit = 1e-8  # minimum timestep ever

goal_rate = 1/3  # rate of result == edge
tolerance = 1/max_flips_limit  # tolerance to stop optimization

bounds = [0.5, 1.0]  # ratio bounds // Exception raised if minimize takes us outside

# ratio bounds from youtube video
#1. d = 2*sqrt(2) * height
#   height = d/(2*sqrt(2)) = r/sqrt(2)
#   height/r = 1/sqrt(2)
#2. d = sqrt(3) * height
#   height = d/sqrt(3) = 2r/sqrt(3)
#   height/r = 2/sqrt(3)
#########################
start_guess = 0.957


# read previous results
def read_results(file='./results.dat'):
    ratios, percents, iters = [], [], []
    if not os.path.exists(file):
        return None
    with open(file, 'r') as f:
        line = f.readline()
        num = 1
        while line:
            res = eval(line)
            assert isinstance(res, tuple), f'line {num} is not a tuple {res}'
            assert all([isinstance(item, (float, int)) for item in res]), f'line {num} contains non-number {res}'
            ratios.append(res[0])
            percents.append(res[1])
            iters.append(res[2])
            line = f.readline()
            num += 1
    return list(zip(ratios, percents, iters))
res = read_results()
if res:
    res = sorted(read_results(), key=lambda r: r[1] / ((r[2] / 3000) ** 2))
    best_ratio, best_percent, nflips = res[0]
else:
    best_ratio = start_guess
    nflips = start_num_flips

sim = Sim(timestep=start_timestep)
sim.flips = nflips


def loss(edge, goal=goal_rate):
    return np.fabs(edge - goal)


def main(ratio, sim):
    logger.info(f"Running ratio {ratio[0]}, for {sim.flips} flips")
    results = {'heads':0, 'tails':0, 'edge':0, 'error':0}
    assert bounds[0] <= ratio <= bounds[1]
    sim.ratio = ratio[0]

    stopped = False
    count = 0
    try:
        for i in tqdm(range(sim.flips)):
            result = sim.flip()
            results[result] += 1
            count = i
    except KeyboardInterrupt:
        stopped = True
    
    edges = results['edge']/(count - results['error'])
    edges = loss(edges)
    
    with open('results.dat', 'a') as f:
        f.write(str((sim.ratio, edges, count-results['error'])) + '\n')

    logger.info(f"ratio:{ratio}, loss:{edges:.10f} results:{results}")

    sim.flips = min(sim.flips+flips_step_rate, max_flips_limit)
    sim.timestep = max(sim.timestep-timestep_rate, min_timestep_limit)

    if stopped:
        raise KeyboardInterrupt
    return edges

logger.info(f"Minimizing between {bounds} starting with ratio {best_ratio}")
optimize_result = minimize(main, x0=best_ratio, bounds=[bounds], args=(sim,), tol=tolerance)

logger.info(optimize_result)

import show_results
