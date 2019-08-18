#!/usr/bin/env python3
from simulator import Sim, p

sim = Sim(
    timestep=1/2000.,  # if using p.GUI, recommend increase this to at least 1/100
    sim_type=p.GUI,  # p.GUI, p.DIRECT
    ratio=.956,  # height/radius_o
)


while True:
    # run a single iteration of the sim
    try:
        result = sim.flip()
        print('*********', result)
    except KeyboardInterrupt:
        break
sim.end()
