#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray

class HolonomicController(Node):

    def __init__(self):
        super().__init__('holonomic_controller')

        # Robot parameters
        self.wheel_radius = 0.0725
        self.L = 0.35
        self.W = 0.35

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10)

        self.publisher = self.create_publisher(
            Float64MultiArray,
            '/wheel_controller/commands',
            10)

        self.get_logger().info("Holonomic controller started")

    def cmd_callback(self, msg):

        vx = msg.linear.x
        vy = msg.linear.y
        wz = msg.angular.z

        r = self.wheel_radius
        k = self.L + self.W

        # mecanum/omni inverse kinematics
        fl = (vx - vy - k*wz) / r
        fr = (vx + vy + k*wz) / r
        bl = (vx + vy - k*wz) / r
        br = (vx - vy + k*wz) / r

        wheel_cmd = Float64MultiArray()
        wheel_cmd.data = [fl, fr, bl, br]

        self.publisher.publish(wheel_cmd)

def main(args=None):
    rclpy.init(args=args)
    node = HolonomicController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()