
import numpy as np
import kinematic_model
import os

model = kinematic_model.KinematicCarMotionModel(0.33) #length 1
# kinematic_model.KinematicCarMotionModel.compute_changes(model, np.zeros((4,3)), np.zeros((4,2)), 0.1)

kinematic_model.KinematicCarMotionModel.apply_deterministic_motion_model(model, np.array([[0.0, 0.0, 0.0]]), 2.0, np.pi / 4, 1.0)
kinematic_model.KinematicCarMotionModel.apply_motion_model(model,np.zeros((100000, 3)), 0, 0, 0.1)