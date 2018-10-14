#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 15:42:03 2018

@author: Tim Olson
"""

from backend import *

sim = Sim(
    flips = 100,  # number of coin flips to perform
    timestep = 1/1000.,  # if using p.GUI, recommend increase this to at least 1/100
    sim_type = p.DIRECT,  # p.GUI, p.DIRECT
    ratio = 1/1,  # height/radius_o
)

results = {'heads':0, 'tails':0, 'edge':0, 'error':0}

# loop through flips
for i in range(sim.flips):
    # show when running
    if int(i/5) == i/5:
        print('.', end='', flush=True)

    # sim must be reset before each iteration
    sim.reset_sim()
    # run a single iteration of the sim
    result = sim.single_iter(
        # generate starting conditions with random functions
        start_orien(),  # coin orientation
        start_velocity(),  # coin linear velocity
        start_rotation(),  # coin angular velocity
        start_position()  # coin position
        )

    # store the flip's result
    results[result] += 1

# show results
print('\n' + str(results))
