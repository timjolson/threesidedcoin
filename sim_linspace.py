#!/usr/bin/env python3
from simulator import *
import logging
from tqdm import tqdm
import os
import numpy as np

logging.basicConfig(filename='./sim_linspace.log', filemode='w', level=logging.INFO, format="%(filename)s:%(funcName)s:%(lineno)s:%(msg)s")

#########################
num_flips = 25_000
timestep = .0002

goal_rate = 1/3  # rate of result == edge
tolerance = 1/num_flips  # tolerance to stop searching

num_points = 20
bounds = [1.008, 1.04]  # ratio bounds to evaluate within
#########################

sim = Sim(timestep=timestep)
sim.flips = num_flips


def loss(edge, goal=goal_rate):
    return np.fabs(edge - goal)


def main(ratio, sim):
    logger.info(f"Running ratio {ratio}, for {sim.flips} flips, timestep {sim.timestep}")
    results = {'heads':0, 'tails':0, 'edge':0, 'error':0}
    assert bounds[0] <= ratio <= bounds[1]
    sim.ratio = ratio

    stopped = False
    count = 0
    try:
        #bar = tqdm(range(sim.flips))
        #for i in bar:
        for i in tqdm(range(sim.flips), leave=False):
            result = sim.flip()
            results[result] += 1
            count += 1
    except KeyboardInterrupt:
        stopped = True
    
    #bar.clear()
    #bar.close()
    
    edges = results['edge']/(count - results['error'])
    edges = loss(edges)
    
    with open('results.dat', 'a') as f:
        f.write(str((sim.ratio, edges, count-results['error'])) + '\n')

    logger.info(f"ratio:{ratio}, loss:{edges:.10f} results:{results}")

    if stopped:
        raise KeyboardInterrupt
    return edges

_points = list(np.linspace(*bounds, num_points))
# alternate values, outside in, within bounds
points = []
while _points:
    points.append(_points.pop(0))
    try:
        points.append(_points.pop(-1))
    except IndexError:
        pass

st = f"Evaluating {num_points} ratios between {bounds}, flips {num_flips}, timestep {timestep}"
logger.info(st)
print(st)
for p in tqdm(points):
    #print(f'Ratio {p}: {main(p, sim)}')
    main(p, sim)

import show_results
