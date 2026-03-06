#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import math
import json

class CmdVelSerial(Node):

    def __init__(self):
        super().__init__("cmdvel_serial")

        self.declare_parameter("port", "/dev/ttyUSB0")
        self.declare_parameter("baud", 115200)

        port = self.get_parameter("port").value
        baud = self.get_parameter("baud").value

        self.ser = serial.Serial(port, baud, timeout=1)
        self.get_logger().info(f"Serial connected {port}")

        self.create_subscription(Twist, "/cmd_vel", self.cmd_callback, 10)

    def read_arduino(self):
        self.get_logger().info(f"in funcyton")
   

    def cmd_callback(self, msg):

        vx = msg.linear.x
        vy = msg.linear.y
        wz = msg.angular.z
        strength = (math.sqrt(vx*vx + vy*vy))
        theta = (math.degrees(math.atan2(vy,vx)))
        if theta<0:
            theta += 360
        


        # --- scale to 0-100 ---
        SSS = int(max(0, min(50, (strength) * 200)))
        RRR = int(max(0, min(50, (abs(wz)) * 20)))
        AAA = int(max(0, min(359, theta)))  
        TT = 0
        if SSS == 0:
         AAA = 400

        frame = f"S{RRR:03d}{AAA:03d}{SSS:03d}{TT:02d}"

        data = {"LOC": frame}  
        
        if strength == 0:
            theta = 400    
        self.ser.write((json.dumps(data) + '*').encode())
        self.read_arduino
        try:
            self.get_logger().info(f"in try")
            while self.arduino.in_waiting:
                self.get_logger().info(f"in while")
                line = self.arduino.readline().decode().strip()
                if line:
                    self.get_logger().info(f"Arduino: {line}")
        except Exception:
            pass 

            

def main():
    rclpy.init()
    node = CmdVelSerial()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
