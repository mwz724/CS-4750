#!/usr/bin/env python3

import rospy
import tf2_ros
import tf_conversions
import numpy as np
from sensor_msgs.msg import JointState
from tf.transformations import quaternion_from_matrix, translation_from_matrix
import geometry_msgs.msg

class Foward_Kinematics_Broadcaster:

    def __init__(self):
        rospy.loginfo("Initialize Joint State subscriber")
        self.subscriber = rospy.Subscriber('/wx250s/joint_states', JointState, self.callback)

    def compute_fk(self, q_waist, q_shoulder, q_elbow):
        L0 = 0.072
        L1 = 0.039
        L2 = 0.250
        L3 = 0.049
        L4 = 0.409

        '''Feel free to comment out the following once you compute your own base_E_gripper'''
        base_E_shoulder = self.dh_transform(0, 0, L0+L1, q_waist+np.pi)
        shoulder_E_Uarm = self.dh_transform(np.pi/2, 0, 0, np.arctan2(L3, L2) + np.pi/2 + q_shoulder)
        Uarm_E_Uforearm = self.dh_transform(0, np.sqrt(L3**2 + L2**2), 0, np.pi/2 - np.arctan2(L3,L2) + q_elbow)
        Uforearm_E_gripper = self.dh_transform(np.pi/2, L4, 0, 0)
        '''
        Input: 
            q_waist: value for waist joint, the first slider on joint_state_publisher_gui controls this
            q_shoulder: value for shoulder joint
            q_elbow: value for elbow joint
        Return: 
            base_E_shoulder:     An numpy matrix (4x4) that represent the forward kinematics from base_link to shoulder_link
            shoulder_E_Uarm:     An numpy matrix (4x4) that represent the forward kinematics from shoulder_link to upper_arm_link
            Uarm_E_Uforearm:     An numpy matrix (4x4) that represent the forward kinematics from upper_arm_link to upper_forearm_link
            Uforearm_E_gripper:  An numpy matrix (4x4) that represent the forward kinmeatics from upper_forearm_link to ee_gripper_link

        Hint: 
            + Define a helper function that computes the transformation matrix from frame {i-1} to frame {i} given the 4 D-H parameters:
                i.e. define a function dh_transform(self, alpha, a, d, phi) that returns the transformation matrix matrix (numpy matrix (4x4))
            + Feel free to use np.sin() and np.cos().
        '''
        '''Compute the forward kinematics transformation matrices for Widowx250'''

        
        # BEGIN SOLUTION 2.2

        # END SOLUTION 
        
        return base_E_shoulder, shoulder_E_Uarm, Uarm_E_Uforearm, Uforearm_E_gripper

    def dh_transform(self, alpha, a, d, phi):
        return np.matrix([[np.cos(phi),-np.sin(phi),0,a],
                          [np.sin(phi)*np.cos(alpha),np.cos(phi)*np.cos(alpha),-np.sin(alpha), -d*np.sin(alpha)],
                          [np.sin(phi)*np.sin(alpha),np.cos(phi)*np.sin(alpha),np.cos(alpha), d*np.cos(alpha)],
                          [0,0,0,1]])

    def callback(self, msg):
        joints_angle = msg.position
        q_waist = joints_angle[0]
        q_shoulder = joints_angle[1]
        q_elbow = joints_angle[2]

        base_E_shoulder, shoulder_E_Uarm, Uarm_E_Uforearm, Uforearm_E_gripper = self.compute_fk(q_waist, q_shoulder, q_elbow)
        base_E_gripper = base_E_shoulder * shoulder_E_Uarm * Uarm_E_Uforearm * Uforearm_E_gripper


        q = quaternion_from_matrix(base_E_gripper)
        translation = translation_from_matrix(base_E_gripper)

        br = tf2_ros.TransformBroadcaster()
        t = geometry_msgs.msg.TransformStamped()

        t.header.stamp = rospy.Time.now()
        t.header.frame_id = "wx250s/base_link"
        t.child_frame_id = "fk_frame"
        t.transform.translation.x = translation[0]
        t.transform.translation.y = translation[1]
        t.transform.translation.z = translation[2]
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        br.sendTransform(t)

        

