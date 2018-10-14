#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 15:42:03 2018

@author: t
"""

from backend import *

sim = Sim(
    flips = 100,  # number of coin flips to perform
    timestep = 1/1000.,  # if using p.GUI, recommend increase this to at least 1/100
    sim_type = p.DIRECT,  # p.GUI, p.DIRECT, p.SHARED_MEMORY
    ratio = 1/1,  # height/radius_o
)

results = {'heads':0, 'tails':0, 'edge':0, 'error':0}

for i in range(sim.flips):
    if int(i/5) == i/5:
        print('.', end='', flush=True)

    sim.reset_sim()
    result = sim.single_iter(
        start_orien(), start_velocity(), start_rotation(), start_position()
        )

    results[result] += 1

print('\n' + str(results))
