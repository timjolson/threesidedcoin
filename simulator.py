#!/usr/bin/env python3
import pybullet as p
import pybullet_data
import numpy as np
import time
import logging
import os
logger = logging.getLogger(__name__)


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
    def __init__(self, **kwargs):
        self.timestep = kwargs.pop('timestep', 1/1000.)
        self.table_radius = kwargs.pop('table_radius', 14)  # distance allowed to roll on edge
        self.gravity = kwargs.pop('gravity', 9.81)
        self.restitution = kwargs.pop('restitution', 0.8)
        self.spinningFriction = kwargs.pop('spinning_friction', 0.001)
        self.rollingFriction = kwargs.pop('rolling_friction', 0.01)
        self.lateralFriction = kwargs.pop('lateral_friction', 1)
        self.sim_type = kwargs.pop('sim_type', p.DIRECT)
        self.error_timeout = kwargs.pop('timeout', 15)  # max time a single flip is allowed to run
        self.file = kwargs.pop('file', "cylinder.urdf")  # urdf to use as base
        self.rolling_min_KE = kwargs.pop('rolling_min_KE', 0.1)  # min kinetic energy estimate to stop sim when rolling
        self.flat_min_KE = kwargs.pop('flat_min_KE', 0.26)  # min kinetic energy estimate to stop sim when approaching flat side
        self._radius_o = kwargs.pop('radius_o', 0.5)
        self._radius_i = kwargs.pop('radius_i', 0.0)
        self._ratio = kwargs.pop('ratio', .956)  # thickness / outer radius
        assert not kwargs, f'extra kwargs: {kwargs}'

        self.update_inertia()

        self.cid = p.connect(self.sim_type)  # p.GUI \ p.DIRECT \ p.SHARED_MEMORY
        assert self.cid >= 0, 'p.connect failed'
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
        self.ixx = (1/12)*self.mass*(3*(self.radius_o**2 + self.radius_i**2) + (self.ratio * self.radius_o)**2)
        self.iyy = self.ixx
        self.izz = .5*self.mass*(self.radius_o**2 + self.radius_i**2)
        self.urdf_flag = True

    def KE(self, linVel, angVel):
    #    KE = 0.5 * mass * np.square(linVel) + 0.5 * np.array([ixx, iyy, izz]) * np.square(angVel)
    #    constants removed
        KE = np.square(linVel) + np.array([self.ixx, self.iyy, self.izz]) * np.square(angVel)
        KE = np.sqrt(KE.dot(KE))
        return KE

    def PE(self, objID):
    #    return mass*(pos[2])*gravity
    #    constants removed
        return p.getBasePositionAndOrientation(objID, physicsClientId=self.cid)[0][2]
    
    def reset_sim(self):
        p.resetSimulation(physicsClientId=self.cid)
        p.setGravity(0, 0, -self.gravity, physicsClientId=self.cid)
        p.setRealTimeSimulation(self.sim_type == p.GUI, physicsClientId=self.cid)
        p.setTimeStep(self.timestep, physicsClientId=self.cid)
        
        self.tableId = p.loadURDF("plane.urdf", physicsClientId=self.cid)
        assert self.tableId >= 0, f'problem making plane for cid{self.cid}'

    def make_coin(self, start_pos, start_orn):
        out_lines = []
        start_orn = p.getQuaternionFromEuler(start_orn)

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
                    else:
                        out_lines.append(line)
            self.adjusted_file_name = ''.join(self.file.split('.')[:-1])+\
                                      f"_ratio_{self.ratio}_ro_{self.radius_o}_ri_{self.radius_i}."+\
                                      self.file.split('.')[-1]
            with open(self.adjusted_file_name, 'w') as f:
                for line in out_lines:
                    f.write(line)

        self.cyl = p.loadURDF(self.adjusted_file_name, start_pos, start_orn, physicsClientId=self.cid)
        if self.urdf_flag is True:
            os.remove(self.adjusted_file_name)
        self.urdf_flag = False

    def init_sim(self, start_orn, start_vel, start_rot, start_pos):
        with open(f'last_run_{self.cid}.tmp', 'w') as f:
            f.write(f"{start_orn, start_vel, start_rot, start_pos}")
        
        self.make_coin(start_pos, start_orn)
        p.resetBaseVelocity(self.cyl, start_vel, start_rot, physicsClientId=self.cid)

        p.changeDynamics(self.cyl, -1, physicsClientId=self.cid,
                         restitution=self.restitution,
                         spinningFriction=self.spinningFriction,
                         rollingFriction=self.rollingFriction,
                         lateralFriction=self.lateralFriction)

    def end(self):
        logger.info(f'Sim {self.cid} Disconnecting')
        try:
            p.disconnect(physicsClientId=self.cid)
        except Exception:
            pass
    __del__ = end

    def flip(self, start_orn=None, start_vel=None,
             start_rot=None, start_pos=None, **kwargs):
        start_orn = start_orn or start_orien()
        start_vel = start_vel or start_velocity()
        start_rot = start_rot or start_rotation()
        start_pos = start_pos or start_position()

        for k,v in kwargs.items():
            setattr(self, k, v)

        sim_time = 0
        self.reset_sim()
        self.init_sim(start_orn, start_vel, start_rot, start_pos)

        while sim_time < self.error_timeout:
            sim_time += self.timestep
            if self.sim_type == p.GUI:
                time.sleep(self.timestep)  # Time in seconds.
            else:
                p.stepSimulation(physicsClientId=self.cid)

            # current position, orientation of coin
            pos, orn = p.getBasePositionAndOrientation(self.cyl, physicsClientId=self.cid)

            if pos[2] < self.radius_o*.98:
                # tilted over
                orn = p.getEulerFromQuaternion(orn)
                vel = p.getBaseVelocity(self.cyl, physicsClientId=self.cid)
                linVel, angVel = vel[0], vel[1]

                if self.KE(linVel, angVel) < self.flat_min_KE:
                    # if Kinetic Energy is low enough to stop on a side
                    side = np.sqrt(orn[0]**2 + orn[1]**2)
                    # use angle of cylinder to decide which face is up
                    if side < 1:
                        return 'heads'
                    else:
                        return 'tails'
            elif np.sqrt(pos[0] ** 2 + pos[1] ** 2) > self.table_radius:
                # coin rolled past edge
                return 'edge'
            elif pos[2] < -self.radius_o:
                # coin is below table
                return 'error'
            else:
                # rolling
                vel = p.getBaseVelocity(self.cyl, physicsClientId=self.cid)
                linVel, angVel = vel[0], vel[1]

                if self.KE(linVel, angVel) < self.rolling_min_KE:
                    # Kinetic Energy low enough to call the result, or rolled past table edge
                    return 'edge'

        # loop finished
        return 'error'
