#!/usr/bin/env python3

import math
import rospy
from moveit_msgs.msg import DisplayTrajectory
from moveit_commander import (MoveGroupCommander,
                              RobotCommander,
                              PlanningSceneInterface)

def show_joint_values(mgc):
    """Shows joint values with rospy log info."""
    rjs = mgc.get_current_joint_values()
    rospy.loginfo("Current joint angles.")
    rospy.loginfo("j1: %f", rjs[0])
    rospy.loginfo("j2: %f", rjs[1])
    rospy.loginfo("j3: %f", rjs[2])
    rospy.loginfo("j4: %f", rjs[3])
    rospy.loginfo("j5: %f", rjs[4])
    rospy.loginfo("j6: %f", rjs[5])
    rospy.loginfo("j7: %f", rjs[6])


def go_with_joint_values(mgc, jvs):
    """Executes the motions with joint values set."""
    mgc.set_joint_value_target(jvs)
    mgc.go(wait=True)
    rospy.sleep(rospy.Duration.from_sec(0.5))


def demo_wavearms():
    """Executes sda5f whole body motions."""
    rospy.init_node(
        "moveit_command_sender",
        disable_signals=True,
        log_level=rospy.DEBUG)
    rospy.sleep(rospy.Duration.from_sec(2))

    torso = MoveGroupCommander("torso")
    larm = MoveGroupCommander("arm_left")
    rarm = MoveGroupCommander("arm_right")
    arms = MoveGroupCommander("arms")
    robot = RobotCommander()
    scene = PlanningSceneInterface()
    display_trajectory_publisher = rospy.Publisher(
        '/move_group/display_planned_path',
        DisplayTrajectory,
        queue_size=20)

    arms.set_max_velocity_scaling_factor(1.0)
    arms.set_max_acceleration_scaling_factor(1.0)
    torso.set_max_velocity_scaling_factor(0.8)
    torso.set_max_acceleration_scaling_factor(0.8)

    # Initializing whole body joint values
    initial_arms_jvs = [
        math.radians(170.0),
        math.radians(-90.0),
        math.radians(-90.0),
        math.radians(-10.0),
        math.radians(0.0),
        math.radians(-80.0),
        math.radians(0.0),
        math.radians(170.0),
        math.radians(-90.0),
        math.radians(-90.0),
        math.radians(-10.0),
        math.radians(0.0),
        math.radians(-80.0),
        math.radians(0.0)]
    wave_arms_jvs = [
        math.radians(150.0),
        math.radians(-90.0),
        math.radians(-90.0),
        math.radians(50.0),
        math.radians(0.0),
        math.radians(20.0),
        math.radians(0.0),
        math.radians(150.0),
        math.radians(-90.0),
        math.radians(-90.0),
        math.radians(50.0),
        math.radians(0.0),
        math.radians(20.0),
        math.radians(0.0)]

    initial_torso_jvs = [0., 0.]
    go_with_joint_values(torso, initial_torso_jvs)
    while not rospy.is_shutdown():
        rospy.loginfo("Initializing whole body joints...")
        go_with_joint_values(arms, initial_arms_jvs)

        larm_initial_pose = larm.get_current_pose().pose
        larm_initial_joint_values = larm.get_current_joint_values()
        rospy.loginfo("larm initial configuration")
        rospy.loginfo(larm_initial_pose)
        rospy.loginfo(larm_initial_joint_values)
        rarm_initial_pose = rarm.get_current_pose().pose
        rarm_initial_joint_values = rarm.get_current_joint_values()
        rospy.loginfo("rarm initial configuration")
        rospy.loginfo(rarm_initial_pose)
        rospy.loginfo(rarm_initial_joint_values)

        go_with_joint_values(arms, wave_arms_jvs)

    rospy.signal_shutdown("Finished.")


if __name__ == '__main__':
    try:
        demo_wavearms()
    except rospy.ROSInterruptException:
        pass
