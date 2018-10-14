# threesidedcoin
A pybullet simulation to optimize 3-sided coin geometry.

Windows OS's have a hard time with pybullet, use Ubuntu if possible.

## install
Highly recommend installing in a virtualenv to keep from polluting your system.
Install may take a long time, as several dependencies are heavy.

    git clone https://github.com/timjolson/threesidedcoin
    cd threesidedcoin
    pip install -e .

## scripts
    backend.py - supporting functions to run simulation, contains class Sim
  
    show_results.py - displays results and data fitted curve, prints predicted optimal geometry
  
    sim_simple.py - most basic example of running a simulation
  
    sim_linspace.py - run sim for a numpy.linspace of geometries
  
    sim_minimize.py - run sim, increasing number of flips and decreasing simulation timestep,
                    while using scipy.optimize.minimize. With low accuracy/repeatability, scipy algorithm
                    ends up outside the bounds, errors out.
                    
    sim_multiprocess_linspace.py - UNRELIABLE. Uses multiprocessing to run sim_linspace(s).

## files
    sim.log - log file of sims run
    
    cylinder_ref.urdf - a reference URDF file for the coin geometry
    
    cylinder.urdf - URDF file built for each geometry, generated and loaded when needed

## results
    results.dat - log of sim results: (ratio, error of landing on edge rate, successful flips)

<img width="600" src="/results.png">
