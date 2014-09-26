#!/usr/bin/python

import sys

import rospkg
import rospy
from std_msgs.msg import (
    String,
)
from sensor_msgs.msg import (
    Image,
)

import baxter_interface

import cv
import cv_bridge
import learn_play


class EEGExp(object):
    """
    Main class for EEG Experiment
    """

    def __init__(self, limb):

        self._rp = rospkg.RosPack()
        self._config_path = self._rp.get_path('eeg_baxter') + '/config/'
        self._images_path = self._rp.get_path('eeg_baxter') + '/share/images/'

        self._cheeky_face_path = self._images_path + "cheeky_face.jpg"
        self._good_face_path = self._images_path + "good_face.jpg"
        self._angry_face_path = self._images_path + "angry_face.jpg"
        self._worried_face_path = self._images_path + "worried_face.jpg"
        self._hilarious_face_path = self._images_path + "hilarious_face.jpg"

        self._limb = limb
        self._baxter_limb = baxter_interface.Limb(self._limb)
        self._baxter_gripper = baxter_interface.Gripper(self._limb)

        print "Calibrating gripper..."
        self._baxter_gripper.calibrate()

        if (not self._check_config()):
            exit(0)
            # self._read_config(self._config_file_path)

    def _check_config(self):
        ri = ""
        while (1):
            ri = raw_input("Have you calibrated the arm? [y/n] ")
            if ri.lower() == "y":
                print "Awesome. Carry on."
                return True
            elif ri.lower() == "n":
                print ">> run `rosrun learn_play calibrate.py` first! <<"
                return False

    def _read_config(self, file):
        """
        Read positions from config file.
        """

        print "Reading positions from file."
        f = open(file, 'r')
        lines = f.readlines()
        splitted = [line.split("=") for line in lines]
        self._default_pos = eval(splitted.pop(0)[1])
        self._neutral_pos = eval(splitted.pop(0)[1])
        for x in range(8):
            for y in range(8):
                # This must be really slow
                self._chess_pos[(x, y)] = eval(splitted.pop(0)[1])
        print "Positions are in memory."
        f.close()

    def gripper_open(self, percentage):
        if percentage < 100:
            return self._baxter_gripper.command_position(percentage)
        else:
            return False

    def send_image(self, path):
        """
        Send the image located at the specified path to the head
        display on Baxter.

        @param path: path to the image file to load and send
        """
        img = cv.LoadImage(path)
        msg = cv_bridge.CvBridge().cv_to_imgmsg(img, encoding="bgr8")
        pub = rospy.Publisher('/robot/xdisplay', Image, latch=True)
        pub.publish(msg)
        # Sleep to allow for image to be published.
        # rospy.sleep(1)

    def head_turn(self, direction=-1):
        """
        -1 = left, 1 = right
        """
        self._baxter_head.set_pan(direction*0.8, 50)
        self._baxter_head.set_pan(0.0, 10)


def main():

    limb = "right"
    rospy.init_node('eeg_baxter_%s' % (limb))
    exp = EEGExp(limb)

    while(1):
        exp.send_image(exp._angry_face_path)
        rospy.sleep(2.0)
        exp.send_image(exp._cheeky_face_path)
        rospy.sleep(2.0)
        exp.send_image(exp._good_face_path)
        rospy.sleep(2.0)
        exp.send_image(exp._hilarious_face_path)
        rospy.sleep(2.0)
        exp.send_image(exp._worried_face_path)
        rospy.sleep(2.0)



if __name__ == "__main__":
    main()
