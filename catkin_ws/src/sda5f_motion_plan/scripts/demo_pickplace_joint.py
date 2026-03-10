#!/usr/bin/env python3

import rospy
import queue
from threading import Thread
from moveit_msgs.msg import DisplayTrajectory
from moveit_commander import (MoveGroupCommander,
                              RobotCommander,
                              PlanningSceneInterface)
from tf.transformations import (quaternion_from_euler,
                                euler_from_quaternion)
from geometry_msgs.msg import Pose, Quaternion, Vector3

from industrial_msgs.msg import RobotStatus
from sda5f_motion_plan.srv import SetCommand
from sda5f_motion_plan.msg import OnRobotRGInput
from sda5f_motion_plan.msg import OnRobotVGInput

sda5f_e_stopped = 0
sda5f_motion_possible = 0
sda5f_in_motion = 0
rg6_status = 0


def save_sda5f_status(status):
    """Saves the current sda5f status."""
    global sda5f_e_stopped, sda5f_motion_possible, sda5f_in_motion
    sda5f_e_stopped = status.e_stopped.val
    sda5f_motion_possible = status.motion_possible.val
    sda5f_in_motion = status.in_motion.val
    # rospy.loginfo("sda5f: "+str(sda5f_in_motion))


def wait_for_sda5f_ready():
    """Waits for the sda5f ready."""
    while True:
        rospy.sleep(rospy.Duration.from_sec(0.1))
        if sda5f_in_motion == 0:
            break


def save_rg6_status(status):
    """Saves the current rg6 status."""
    global rg6_status
    rg6_status = status.gSTA
    # rospy.loginfo("rg6: "+str(rg6_in_motion))


def wait_for_rg6_ready():
    """Waits for the rg6 ready."""
    while True:
        rospy.sleep(rospy.Duration.from_sec(0.1))
        if rg6_status != 1:
            break


class ThreadWithReturnValue(Thread):
    """Overwrites Tread class to get return values."""
    def __init__(
            self,
            group=None,
            target=None,
            name=None,
            args=(),
            kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


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


def gen_arm_pose(currpose, relpos, relori):
    """Generates an arm pose.

    currpose: Pose, current arm pose
    relpos: Vector3, target relative position [m]
    relori: Vector3, target relative orientation [rad]
    """
    target_pose = Pose()
    target_pose.position.x = currpose.position.x + relpos.x
    target_pose.position.y = currpose.position.y + relpos.y
    target_pose.position.z = currpose.position.z + relpos.z
    current_euler = quaternion_to_euler(currpose.orientation)
    target_euler = Vector3()
    target_euler.x = current_euler.x + relori.x
    target_euler.y = current_euler.y + relori.y
    target_euler.z = current_euler.z + relori.z
    target_pose.orientation = euler_to_quaternion(target_euler)
    return target_pose


def go_with_eef_pose(mgc, pose):
    """Executes the motions with a target pose."""
    mgc.set_pose_target(pose)
    mgc.go(wait=True)
    # rospy.sleep(rospy.Duration.from_sec(0.2))
    mgc.stop()
    mgc.clear_pose_targets()


def euler_to_quaternion(euler):
    """Converts euler angles to quaternion.

    euler: geometry_msgs/Vector3
    quaternion: geometry_msgs/Quaternion
    """
    q = quaternion_from_euler(euler.x, euler.y, euler.z)
    return Quaternion(x=q[0], y=q[1], z=q[2], w=q[3])


def quaternion_to_euler(quaternion):
    """Converts quaternion to euler angles.

    quarternion: geometry_msgs/Quaternion
    euler: geometry_msgs/Vector3
    """
    e = euler_from_quaternion(
        (quaternion.x, quaternion.y, quaternion.z, quaternion.w))
    return Vector3(x=e[0], y=e[1], z=e[2])


def demo_pickplace():
    """Executes sda5f whole body motions."""
    global sda5f_e_stopped, sda5f_motion_possible, sda5f_in_motion, rg6_status
    rospy.init_node(
        "moveit_command_sender",
        disable_signals=True,
        log_level=rospy.DEBUG)
    rospy.Subscriber("robot_status", RobotStatus, save_sda5f_status)
    rospy.Subscriber("OnRobotRGInput", OnRobotRGInput, save_rg6_status)
    rospy.sleep(rospy.Duration.from_sec(2))

    if sda5f_e_stopped == 1:
        rospy.loginfo("Error on sda5f: Emergency is activated.\n")
        rospy.signal_shutdown("Finished.")
        rospy.sleep(rospy.Duration.from_sec(1))
        return -1
    if sda5f_motion_possible == 0:
        rospy.loginfo(
            "Error on sda5f: Motion is not possible. Motor is not enabled.")
        rospy.signal_shutdown("Finished.")
        rospy.sleep(rospy.Duration.from_sec(1))
        return -1
    # left (72) or right (104) finger's safety swith is activated
    if (rg6_status == 72) or (rg6_status == 104):
        rospy.loginfo(
            "Error on rg6: Safety circuit 1 is activated so the gripper cannot move."
            " Any of the safety switch is pushed.")
        rospy.signal_shutdown("Finished.")
        rospy.sleep(rospy.Duration.from_sec(1))
        return -1

    rospy.wait_for_service('/onrobot_rg/set_command')
    rospy.wait_for_service('/onrobot_vg/set_command')
    onrobot_rg_setcommand = rospy.ServiceProxy(
        '/onrobot_rg/set_command', SetCommand)
    onrobot_vg_setcommand = rospy.ServiceProxy(
        '/onrobot_vg/set_command', SetCommand)

    larm = MoveGroupCommander("arm_left")
    rarm = MoveGroupCommander("arm_right")
    torso = MoveGroupCommander("torso")
    robot = RobotCommander()
    display_trajectory_publisher = rospy.Publisher(
        '/move_group/display_planned_path',
        DisplayTrajectory,
        queue_size=20)
    scene = PlanningSceneInterface()

    larm.set_max_velocity_scaling_factor(0.5)
    larm.set_max_acceleration_scaling_factor(0.5)
    rarm.set_max_velocity_scaling_factor(0.5)
    rarm.set_max_acceleration_scaling_factor(0.5)
    torso.set_max_velocity_scaling_factor(0.5)
    torso.set_max_acceleration_scaling_factor(0.5)

    # Initializing whole body joint values
    initial_left_jvs = [
        -0.8870205879211426,
        -0.4020548462867737,
        2.5387532711029053,
        -1.1657341718673706,
        -1.7188026905059814,
        -1.797049880027771,
        1.774945855140686]
    initial_right_jvs = [
        -0.7407152652740479,
        -0.4013258218765259,
        2.4970169067382812,
        -1.2051773071289062,
        -1.8124666213989258,
        -1.7916895151138306,
        1.1042062044143677]
    initial_torso_jvs = [0., 0.]

    rospy.loginfo("Initializing whole body joints...")
    onrobot_rg_setcommand("700")  # reset
    onrobot_vg_setcommand('r')  # reset
    go_with_joint_values(larm, initial_left_jvs)
    go_with_joint_values(rarm, initial_right_jvs)
    go_with_joint_values(torso, initial_torso_jvs)
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
    rospy.sleep(rospy.Duration.from_sec(1))

    # generate poses
    container_pregrasp_jv_l = [
        -0.801922619342804,
        0.32966917753219604,
        2.580672025680542,
        -0.9104403257369995,
        -1.5893863439559937,
        -1.2823562622070312,
        0.9569960236549377]
    container_grasp_jv_l = [
        -0.7361437082290649,
        0.23239049315452576,
        2.643322229385376,
        -0.8129642009735107,
        -1.7067433595657349,
        -1.2258919477462769,
        0.9572040438652039]
    container_release_jv_l = [
        -0.7883294224739075,
        -0.42820844054222107,
        2.6489417552948,
        -1.0349358320236206,
        -1.9410779476165771,
        -1.7176792621612549,
        1.6614571809768677]
    container_postrelease_jv_l = [
        -0.8870205879211426,
        -0.4020548462867737,
        2.5387532711029053,
        -1.1657341718673706,
        -1.7188026905059814,
        -1.797049880027771,
        1.774945855140686]

    object_pregrasp_jv_r = [
        -0.7407152652740479,
        -0.4013258218765259,
        2.4970169067382812,
        -1.2051773071289062,
        -1.8124666213989258,
        -1.7916895151138306,
        1.1042062044143677]
    object_grasp_jv_r = [
        -0.4392804503440857,
        -0.5212193131446838,
        2.82370924949646,
        -0.7361285090446472,
        -2.426787853240967,
        -1.4180359840393066,
        0.8587952852249146]
    object_release_jv_r = [
        -0.9103036522865295,
        -0.8776496052742004,
        2.5507972240448,
        0.02264520153403282,
        -2.06750226020813,
        -1.672469973564148,
        1.2653261423110962]

    torso_pick_joint_values = [0., 0.]
    torso_place_joint_values = [-0.7, 0.]

    def wait_for_ready(is_ready):
        """Waits for ready."""
        while True:
            rospy.sleep(rospy.Duration.from_sec(0.1))
            if is_ready.get():
                break
        is_ready.put(False)
        return True

    def larm_motions(
            is_ready_larm,
            is_ready_rarm,
            is_ready_leef,
            is_ready_reef,
            is_ready_torso):
        """Defines left arm motions in a thread."""
        rospy.loginfo("larm: start thread")

        rospy.loginfo("larm: pregrasp container")
        go_with_joint_values(larm, container_pregrasp_jv_l)
        rospy.loginfo("larm: grasp container")
        go_with_joint_values(larm, container_grasp_jv_l)
        is_ready_leef.put(True)
        wait_for_ready(is_ready_larm)
        rospy.loginfo("larm: release container")
        go_with_joint_values(larm, container_release_jv_l)
        is_ready_leef.put(True)
        is_ready_rarm.put(True)
        wait_for_ready(is_ready_larm)
        rospy.loginfo("larm: postrelease container")
        go_with_joint_values(larm, container_postrelease_jv_l)

        wait_for_ready(is_ready_larm)
        rospy.loginfo("larm: release container")
        go_with_joint_values(larm, container_release_jv_l)
        is_ready_leef.put(True)
        wait_for_ready(is_ready_larm)
        rospy.loginfo("larm: grasp container")
        go_with_joint_values(larm, container_grasp_jv_l)
        is_ready_leef.put(True)

        return True

    def rarm_motions(
            is_ready_larm,
            is_ready_rarm,
            is_ready_leef,
            is_ready_reef,
            is_ready_torso):
        """Defines right arm motions in a thread."""
        rospy.loginfo("rarm: start thread")

        rospy.loginfo("rarm: pregrasp object")
        go_with_joint_values(rarm, object_pregrasp_jv_r)
        wait_for_ready(is_ready_rarm)
        is_ready_reef.put(True)
        rospy.loginfo("rarm: grasp object")
        go_with_joint_values(rarm, object_grasp_jv_r)
        wait_for_ready(is_ready_rarm)
        rospy.loginfo("rarm: return to pregrasp object")
        go_with_joint_values(rarm, object_pregrasp_jv_r)
        is_ready_torso.put(True)
        wait_for_ready(is_ready_rarm)
        rospy.loginfo("rarm: release object")
        go_with_joint_values(rarm, object_release_jv_r)
        is_ready_reef.put(True)

        wait_for_ready(is_ready_rarm)
        is_ready_reef.put(True)
        wait_for_ready(is_ready_rarm)
        rospy.loginfo("rarm: return to pregrasp object")
        go_with_joint_values(rarm, object_pregrasp_jv_r)
        is_ready_torso.put(True)
        wait_for_ready(is_ready_rarm)
        is_ready_larm.put(True)
        rospy.loginfo("rarm: grasp object")
        go_with_joint_values(rarm, object_grasp_jv_r)
        is_ready_reef.put(True)
        wait_for_ready(is_ready_rarm)
        rospy.loginfo("rarm: pregrasp object")
        go_with_joint_values(rarm, object_pregrasp_jv_r)

        return True

    def leef_motions(
            is_ready_larm,
            is_ready_rarm,
            is_ready_leef,
            is_ready_reef,
            is_ready_torso):
        """Defines left end effector motions in a thread."""
        rospy.loginfo("leef: start thread")

        wait_for_ready(is_ready_leef)
        rospy.loginfo("leef: grasp")
        onrobot_rg_setcommand('c')
        wait_for_rg6_ready()
        is_ready_larm.put(True)
        wait_for_ready(is_ready_leef)
        rospy.loginfo("leef: open")
        onrobot_rg_setcommand("700")
        wait_for_rg6_ready()
        is_ready_larm.put(True)

        wait_for_ready(is_ready_leef)
        rospy.loginfo("leef: grasp")
        onrobot_rg_setcommand('c')
        wait_for_rg6_ready()
        is_ready_larm.put(True)
        rospy.loginfo("leef: open")
        onrobot_rg_setcommand("700")

        return True

    def reef_motions(
            is_ready_larm,
            is_ready_rarm,
            is_ready_leef,
            is_ready_reef,
            is_ready_torso):
        """Defines right end effector motions in a thread."""
        rospy.loginfo("reef: start thread")

        wait_for_ready(is_ready_reef)
        rospy.loginfo("reef: grasp")
        onrobot_vg_setcommand('g')
        is_ready_rarm.put(True)
        wait_for_ready(is_ready_reef)
        rospy.loginfo("reef: release")
        onrobot_vg_setcommand('r')
        is_ready_rarm.put(True)

        wait_for_ready(is_ready_reef)
        rospy.loginfo("reef: grasp")
        onrobot_vg_setcommand('g')
        is_ready_rarm.put(True)
        wait_for_ready(is_ready_reef)
        rospy.loginfo("reef: release")
        onrobot_vg_setcommand('r')
        is_ready_rarm.put(True)

        return True

    def torso_motions(
            is_ready_larm,
            is_ready_rarm,
            is_ready_leef,
            is_ready_reef,
            is_ready_torso):
        """Defines torso motions in a thread."""
        rospy.loginfo("torso: start thread")

        wait_for_ready(is_ready_torso)
        rospy.loginfo("torso: place position")
        go_with_joint_values(torso, torso_place_joint_values)
        is_ready_rarm.put(True)
        wait_for_ready(is_ready_torso)
        rospy.loginfo("torso: pick position")
        go_with_joint_values(torso, torso_pick_joint_values)
        is_ready_rarm.put(True)

        return True

    is_ready_larm = queue.Queue()
    is_ready_rarm = queue.Queue()
    is_ready_leef = queue.Queue()
    is_ready_reef = queue.Queue()
    is_ready_torso = queue.Queue()

    is_ready_larm.put(False)
    is_ready_rarm.put(False)
    is_ready_leef.put(False)
    is_ready_reef.put(False)
    is_ready_torso.put(False)
    # execute pp motions using left arm
    rospy.loginfo("Start sda5f motions...")
    larm_thread = ThreadWithReturnValue(
        target=larm_motions,
        args=(is_ready_larm,
              is_ready_rarm,
              is_ready_leef,
              is_ready_reef,
              is_ready_torso))
    larm_thread.start()
    rarm_thread = ThreadWithReturnValue(
        target=rarm_motions,
        args=(is_ready_larm,
              is_ready_rarm,
              is_ready_leef,
              is_ready_reef,
              is_ready_torso))
    rarm_thread.start()
    leef_thread = ThreadWithReturnValue(
        target=leef_motions,
        args=(is_ready_larm,
              is_ready_rarm,
              is_ready_leef,
              is_ready_reef,
              is_ready_torso))
    leef_thread.start()
    reef_thread = ThreadWithReturnValue(
        target=reef_motions,
        args=(is_ready_larm,
              is_ready_rarm,
              is_ready_leef,
              is_ready_reef,
              is_ready_torso))
    reef_thread.start()
    torso_thread = ThreadWithReturnValue(
        target=torso_motions,
        args=(is_ready_larm,
              is_ready_rarm,
              is_ready_leef,
              is_ready_reef,
              is_ready_torso))
    torso_thread.start()

    while True:
        rospy.sleep(rospy.Duration.from_sec(1))
        if larm_thread.join():
            if rarm_thread.join():
                if leef_thread.join():
                    if reef_thread.join():
                        if torso_thread.join():
                            break

    # initializing whole body joints
    rospy.loginfo("Initializing whole body joints...")
    go_with_joint_values(larm, container_pregrasp_jv_l)
    go_with_joint_values(larm, larm_initial_joint_values)
    go_with_joint_values(rarm, rarm_initial_joint_values)
    go_with_joint_values(torso, torso_pick_joint_values)
    rospy.signal_shutdown("Finished.")


if __name__ == '__main__':
    try:
        demo_pickplace()
    except rospy.ROSInterruptException:
        pass
