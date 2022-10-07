#!/usr/bin/env python
from __future__ import division
from threading import Lock
import numpy as np
from numpy.core.numeric import roll
import rospy

from std_msgs.msg import Float64

import matplotlib.pyplot as plt


class KinematicCarMotionModel:
    """The kinematic car motion model."""

    def __init__(self, car_length, **kwargs):
        """Initialize the kinematic car motion model.

        Args:
            car_length: the length of the car
            **kwargs (object): any number of optional keyword arguments:
                vel_std (float): std dev of the control velocity noise
                alpha_std (float): std dev of the control alpha noise
                x_std (float): std dev of the x position noise
                y_std (float): std dev of the y position noise
                theta_std (float): std dev of the theta noise
        """

        defaults = {
            "vel_std": 0.1,
            "alpha_std": 0.1,
            "x_std": 0.05,
            "y_std": 0.05,
            "theta_std": 0.1,
        }
        if not set(kwargs).issubset(set(defaults)):
            raise ValueError("Invalid keyword argument provided")
        # These next two lines set the instance attributes from the defaults and
        # kwargs dictionaries. For example, the key "vel_std" becomes the
        # instance attribute self.vel_std.
        self.__dict__.update(defaults)
        self.__dict__.update(kwargs)

        if car_length <= 0.0:
            raise ValueError(
                "The model is only defined for defined for positive, non-zero car lengths"
            )
        self.car_length = car_length

    def compute_changes(self, states, controls, dt, alpha_threshold=1e-2):
        """Integrate the (deterministic) kinematic car model.

        Given vectorized states and controls, compute the changes in state when
        applying the control for duration dt.

        If the absolute value of the applied alpha is below alpha_threshold,
        round down to 0. We assume that the steering angle (and therefore the
        orientation component of state) does not change in this case.

        Args:
            states: np.array of states with shape M x 3
            controls: np.array of controls with shape M x 2
            dt (float): control duration

        Returns:
            M x 3 np.array, where the three columns are dx, dy, dtheta

        """
        # BEGIN "QUESTION 1.2" ALT="return np.zeros_like(states, dtype=float)"
        M = len(states)
        changes = np.zeros((M,3))
        x,y,theta,v,alpha,dx,dy,dtheta = (np.zeros(M) for i in range(8))

        L = self.car_length

        x[:] = states[:,0]
        y[:]= states[:,1]
        theta[:] = states[:,2]

        v[:] = controls[:,0]
        alpha[:] = controls[:,1] 
        
        if (dt == 0):
            dx[:] = 0
            dy[:] = 0
            dtheta[:] = 0
        else:
            dtheta = np.where(abs(alpha) < alpha_threshold, 0, (v/L)*np.tan(alpha)*dt)
            dx = np.where(abs(alpha) < alpha_threshold,v*np.cos(theta)*dt,(L/np.tan(alpha))*(np.sin(theta + dtheta) - np.sin(theta)))
            dy = np.where(abs(alpha) < alpha_threshold,v*np.sin(theta)*dt,-(L/np.tan(alpha))*(np.cos(theta + dtheta) - np.cos(theta)))

        # if (abs(alpha) < alpha_threshold):
        #     dx = v*np.cos(theta)*dt
        #     dy = v*np.sin(theta)*dt
        #     dtheta = 0
        # elif (dt == 0):
        #     dx = 0
        #     dy = 0
        #     dtheta = 0
        # else:
        #     dtheta = (v/self.car_length)*np.tan(alpha)*dt
        #     dx = (v*dt/dtheta)*(np.sin(theta + dtheta) - np.sin(theta))
        #     dy = -(v*dt/dtheta)*(np.cos(theta + dtheta) - np.cos(theta))


        changes[:,0] = dx[:]
        changes[:,1] = dy[:]
        changes[:,2] = dtheta[:]

        return changes
        # END

    def apply_deterministic_motion_model(self, states, vel, alpha, dt):
        """Propagate states through the determistic kinematic car motion model.

        Given the nominal control (vel, alpha0 = 0.072
        L1 = 0.039
        L2 = 0.250
        L3 = 0.049
        L4 = 0.409
        ), compute the changes in state 
        and update it to the resulting state.

        NOTE: This function does not have a return value: your implementation
        should modify the states argument in-place with the updated states.

        >>> states = np.ones((3, 2))
        >>> states[2, :] = np.arange(2)  #  modifies the row at index 2
        >>> a = np.array([[1, 2], [3, 4], [5, 6]])
        >>> states[:] = a + a            # modifies states; note the [:]

        Args:
            states: np.array of states with shape M x 3
            vel (float): nominal control velocity
            alpha (float): nominal control steering angle
            dt (float): control duration
        """
        n_particles = states.shape[0]

        # Hint: use same controls for all the particles
        # BEGIN SOLUTION "QUESTION 1.3"
        
        M = len(states)
        x = np.zeros(M)
        y = np.zeros(M)
        theta = np.zeros(M)
        control = np.zeros((M,2))
        control[:,0] = vel
        control[:,1] = alpha

        changes = self.compute_changes(states, control, dt)

        
        x[:] = states[:,0]
        y[:] = states[:,1]
        theta[:] = states[:,2]

        states[:,0] = x + changes[:,0]
        states[:,1] = y + changes[:,1]
        theta[:] = theta[:] + changes[:,2]

        theta[:]= (theta[:] + np.pi) % (2*np.pi) - np.pi
        theta = np.where(theta == -np.pi, theta + 2*np.pi, theta)

        states[:,2] = theta[:]

        # END SOLUTION

    def apply_motion_model(self, states, vel, alpha, dt):
        """Propagate states through the noisy kinematic car motion model.

        Given the nominal control (vel, alpha), sample M noisy controls.
        Then, compute the changes in state with the noisy controls.
        Finally, add noise to the resulting states.

        NOTE: This function does not have a return value: your implementation
        should modify the states argument in-place with the updated states.

        >>> states = np.ones((3, 2))
        >>> states[2, :] = np.arange(2)  #  modifies the row at index 2
        >>> a = np.array([[1, 2], [3, 4], [5, 6]])
        >>> states[:] = a + a            # modifies states; note the [:]

        Args:
            states: np.array of states with shape M x 3
            vel (float): nominal control velocity
            alpha (float): nominal control steering angle
            dt (float): control duration
        """
        n_particles = states.shape[0]

        # Hint: you may find the np.random.normal function useful
        # BEGIN SOLUTION "QUESTION 1.4"
        
        M = len(states)
        x,y,theta = (np.zeros(M) for p in range(3))
    
        vel_distr = np.random.normal(vel, self.vel_std, n_particles)
        alpha_distr = np.random.normal(alpha, self.alpha_std, n_particles)

        control = np.zeros((M,2))
        control[:,0] = vel_distr
        control[:,1] = alpha_distr

        changes = self.compute_changes(states, control, dt)

        changes_distr = np.zeros((M,3))
        changes_distr[:,0] = np.random.normal(changes[:,0], self.x_std, n_particles)
        changes_distr[:,1] = np.random.normal(changes[:,1], self.y_std, n_particles)
        changes_distr[:,2] = np.random.normal(changes[:,2], self.theta_std, n_particles)

        x[:] = states[:,0]
        y[:] = states[:,1]
        theta[:] = states[:,2]

        states[:,0] = x[:] + changes_distr[:,0]
        states[:,1] = y[:] + changes_distr[:,1]
        theta[:] = theta[:] + changes_distr[:,2]

        theta[:]= (theta[:] + np.pi) % (2*np.pi) - np.pi
        theta = np.where(theta == -np.pi, theta + 2*np.pi, theta)

        states[:,2] = theta[:]

        # END SOLUTION
