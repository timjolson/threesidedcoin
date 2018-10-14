#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 14:27:35 2018

@author: t
"""

import pybullet as p
import pybullet_data
import numpy as np
import time, multiprocessing

logger = multiprocessing.get_logger()

def start_orien(deg=360):
    return [deg*np.random.random(), deg*np.random.random(), deg*np.random.random()]

def start_position(height=1.2):
    return [0, 0, height]

def start_velocity(magnitude=10):
    hm = magnitude/2
    return [magnitude*np.random.random()-hm, magnitude*np.random.random()-hm, -magnitude*np.random.random()]

def start_rotation(magnitude=60):
    hm = magnitude/2
    return [magnitude*np.random.random()-hm, magnitude*np.random.random()-hm, magnitude*np.random.random()-hm]


class Sim():
    perc_PE = 0.003  # percent/100 of radius_o to start checking for rolling
    min_KE_rolling = 0.06  # min kinetic energy estimate to stop sim when rolling
    min_KE_flat = 0.26  # min kinetic energy estimate to stop sim when approaching flat side
    urdf_lock = multiprocessing.Lock()
    
    def __init__(self, **kwargs):
        self.flips = 10
        self.timestep = 1/1000.
        self.table_radius = 12  # distance allowed to roll on edge
        self.gravity = 9.81
        self.restitution = 0.8
        self.spinningFriction = 0.001
        self.rollingFriction = 0.001
        self.lateralFriction = 1
        self.sim_type = p.DIRECT
        self.error_timeout = 15
        self.file = "cylinder.urdf"        
        
        pop = []
        for k in kwargs:
            if not isinstance(getattr(self, k, None), (property, type(None))):
                setattr(self, k, kwargs[k])
                pop.append(k)
        for k in pop:
            kwargs.pop(k)
        
        self._radius_o = kwargs.pop('radius_o', 0.5)
        self._radius_i = kwargs.pop('radius_i', 0.0)
        self._ratio = kwargs.pop('ratio', 1/1)
        assert not kwargs, f'extra kwargs: {kwargs}'

        self.urdf_flag = True
        self.update_inertia()
        
        self.cid = p.connect(self.sim_type)  # p.GUI \ p.DIRECT \ p.SHARED_MEMORY
        assert self.cid >= 0, f'p.connect failed'
        p.setAdditionalSearchPath(pybullet_data.getDataPath())

    @property
    def ratio(self):
        return self._ratio

    @ratio.setter
    def ratio(self, ratio):
        self._ratio = ratio
        self.update_inertia()

    @property
    def radius_o(self):
        return self._radius_o

    @radius_o.setter
    def radius_o(self, radius_o):
        self._radius_o = radius_o
        self.update_inertia()

    @property
    def radius_i(self):
        return self._radius_i

    @radius_i.setter
    def radius_i(self, radius_i):
        self._radius_i = radius_i
        self.update_inertia()

    def update_mass(self):
        self.mass = np.pi * (self.radius_o**2 - self.radius_i**2) * (self.ratio * self.radius_o)

    def update_inertia(self):
        self.update_mass()
        self.ixx, self.iyy, self.izz = self.IXX(), self.IYY(), self.IZZ()
        self.urdf_flag = True

    def IXX(self):
        return (1/12)*self.mass*(3*(self.radius_o**2 + self.radius_i**2) + (self.ratio * self.radius_o)**2)

    def IYY(self):
        return self.IXX()

    def IZZ(self):
        return .5*self.mass*(self.radius_o**2 + self.radius_i**2)
    
    def KE(self, linVel, angVel):
    #    KE = 0.5 * mass * np.square(linVel) + 0.5 * np.array([ixx, iyy, izz]) * np.square(angVel)
    #    constants removed
        KE = np.square(linVel) + np.array([self.ixx, self.iyy, self.izz]) * np.square(angVel)
        KE = np.sqrt(KE.dot(KE))
        return KE

    def PE(objID):
    #    return mass*(pos[2])*gravity
    #    constants removed
        return p.getBasePositionAndOrientation(objID, physicsClientId=self.cid)[0][2]
    
    def reset_sim(self):
        p.resetSimulation(physicsClientId=self.cid)
        p.setGravity(0, 0, -self.gravity, physicsClientId=self.cid)
        p.setRealTimeSimulation(self.sim_type == p.GUI, physicsClientId=self.cid)
        p.setTimeStep(self.timestep, physicsClientId=self.cid, )
        
        self.tableId = p.loadURDF("plane.urdf", physicsClientId=self.cid)
        assert self.tableId >= 0, f'problem making plane for cid{self.cid}'

    def make_coin(self, start_pos, start_orn):
        out_lines = []
        
        with self.urdf_lock:
            if self.urdf_flag:
                logger.debug(f'making {self.file}')
                with open(self.file, 'r') as f:
                    for line in f.readlines():
                        if line.startswith('	        <cylinder'):
                            out_lines.append('	        <cylinder length="' +str(self.ratio * self.radius_o) + 
                                             '" radius="' + str(self.radius_o) + '"/>\n')
                        elif line.startswith('        	    <mass'):
                            out_lines.append('        	    <mass value="' +str(self.mass) + '"/>\n')
                        elif line.startswith('        	    <inertia'):
                            out_lines.append('        	    <inertia ixx="' + str(self.ixx) + 
                                             '" ixy="0.0" ixz="0.0" iyy="' + str(self.iyy) + 
                                             '" iyz="0.0" izz="' + str(self.izz) + '"/>\n')
            #            elif line.startswith('        	    <restitution'):
            #                out_lines.append('        	    <restitution value="' + str(self.restitution) + '"/>\n')
            #            elif line.startswith('        	    <rolling_friction'):
            #                out_lines.append('        	    <rolling_friction value="' + str(self.rolling_friction) + '"/>\n')
            #            elif line.startswith('        	    <spinning_friction'):
            #                out_lines.append('        	    <spinning_friction value="' + str(self.spinning_friction) + '"/>\n')
            #            elif line.startswith('        	    <spinning_friction'):
            #                out_lines.append('        	    <spinning_friction value="' + str(self.spinning_friction) + '"/>\n')
                        else:
                            out_lines.append(line)
                with open(self.file, 'w') as f:
                    for line in out_lines:
                        f.write(line)

                self.urdf_flag = False
            
            start_orn = p.getQuaternionFromEuler(start_orn)
            self.cyl = p.loadURDF(self.file, start_pos, start_orn, physicsClientId=self.cid)

    def init_sim(self, start_orn, start_vel, start_rot, start_pos):
        with open(f'last_run_{self.cid}.tmp', 'w') as f:
            f.write(f"{start_orn, start_vel, start_rot, start_pos}")
        
        self.make_coin(start_pos, start_orn)
        p.resetBaseVelocity(self.cyl, start_vel, start_rot, physicsClientId=self.cid)

#        p.changeDynamics(tableId,-1,restitution=self.table_restitution)
        p.changeDynamics(self.cyl, -1, physicsClientId=self.cid,
                         restitution=self.restitution,
                         spinningFriction=self.spinningFriction,
                         rollingFriction=self.rollingFriction,
                         lateralFriction=self.lateralFriction)

    def end(self):
        logger.info(f'Sim {self.cid} Disconnecting')
        p.disconnect(physicsClientId=self.cid)

    def single_iter(self, start_orn=start_orien(), start_vel=start_velocity(),
                    start_rot=start_rotation(), start_pos=start_position()):

        sim_time = 0
        self.reset_sim()
        self.init_sim(start_orn, start_vel, start_rot, start_pos)

        result = None
        
        while result is None and sim_time<self.error_timeout:
            sim_time += self.timestep
            if (self.sim_type==p.GUI):
                time.sleep(self.timestep)  # Time in seconds.
            else:
                p.stepSimulation(physicsClientId=self.cid)

            pos, orn = p.getBasePositionAndOrientation(self.cyl, physicsClientId=self.cid)

#            vel = p.getBaseVelocity(cyl)
#            linVel, angVel = vel[0], vel[1]
#            ke = KE(linVel, angVel, self)
#            print(f"ke: {ke}")

            if pos[2] < self.radius_o*.9:
                orn = p.getEulerFromQuaternion(orn)
                vel = p.getBaseVelocity(self.cyl, physicsClientId=self.cid)
                linVel, angVel = vel[0], vel[1]

                if self.KE(linVel, angVel) < self.min_KE_flat:
                    side = np.sqrt(orn[0]**2 + orn[1]**2)
                    if side<1:
                        result = 'heads'
                    else:
                        result = 'tails'

            elif self.radius_o*(1-self.perc_PE) < pos[2] < self.radius_o*(1+self.perc_PE):  #: and \
                # np.fabs(np.sqrt(orn[0]**2 + orn[1]**2) - np.pi/2) < .1:
                vel = p.getBaseVelocity(self.cyl, physicsClientId=self.cid)
                linVel, angVel = vel[0], vel[1]

                if self.KE(linVel, angVel) < self.min_KE_rolling or \
                            np.sqrt(pos[0]**2 + pos[1]**2) > self.table_radius:                    
                    result = 'edge'
            elif np.sqrt(pos[0]**2 + pos[1]**2) > self.table_radius*1.1:
                result = 'edge'
            elif pos[2] < -self.radius_o:
                result = 'error'

        if result is None:
            result = 'error'

        # loop finished
        return result


__all__ = ['Sim', 'start_orien', 'start_position', 'start_velocity', 'start_rotation', 'multiprocessing', 'np', 'p']
