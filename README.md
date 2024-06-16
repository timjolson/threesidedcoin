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
    simulator.py - supporting functions to run simulation, contains class Sim
  
    show_results.py - displays results and predicted optimal geometry, saves results.png
  
    sim_simple.py - basic example of running a simulation
    
    sim_minimize.py - run sim, use scipy.optimize.minimize to find solution; 
                      each iteration increases number of flips, decreases timestep
                      
    sim_linspace.py - run sim on a distribution of ratios

## files
    sim_*.log - log file of sims run
    
    cylinder_ref.urdf - a reference URDF file for the coin geometry
    
    cylinder.urdf - URDF file built for each geometry, generated and loaded when needed

## results
    results.dat - log of sim results: (ratio, error of landing on edge rate, successful flips)

<img width="600" src="/results.png">
