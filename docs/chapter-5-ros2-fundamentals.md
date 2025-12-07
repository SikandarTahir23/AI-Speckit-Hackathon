# Chapter 5: ROS 2 Fundamentals

## Learning Objectives

By the end of this chapter, you will be able to:

*   Understand the core architecture of ROS 2.
*   Define and differentiate between ROS 2 nodes, topics, services, actions, and parameters.
*   Develop basic publisher and subscriber programs in Python.
*   Utilize essential ROS 2 command-line tools for introspection and debugging.
*   Appreciate the advantages of ROS 2 over its predecessor, ROS 1.

## Introduction

ROS 2 (Robot Operating System 2) is an open-source, meta-operating system for robots. It provides a flexible framework for writing robot software, offering tools, libraries, and conventions that simplify the development of complex robotic applications. Building upon the success of ROS 1, ROS 2 was re-architected to address critical limitations, including real-time control, multi-robot systems, and improved security. It is widely adopted in research and industry for everything from autonomous vehicles and industrial robots to drones and humanoid assistants.

**Advantages of ROS 2 over ROS 1:**

*   **DDS (Data Distribution Service) as Middleware**: ROS 2 uses DDS, providing native support for real-time communication, quality of service (QoS) policies, and multi-robot capabilities.
*   **Multi-Platform Support**: Improved support for Windows, macOS, and various Linux distributions.
*   **Real-time Capabilities**: Enhanced determinism and reduced latency for performance-critical applications.
*   **Security**: Built-in security features for authentication, authorization, and encryption.
*   **No Central Master**: Decentralized architecture improves robustness and scalability.

## Core Concepts

### ROS 2 Architecture

ROS 2's architecture is based on a distributed network of independent executable processes (nodes) that communicate with each other.

*   **Nodes**: Independent executable processes that perform specific tasks (e.g., a camera driver, a motor controller, a navigation algorithm).
*   **Topics**: A publish-subscribe mechanism for nodes to exchange asynchronous, continuous streams of messages (e.g., sensor data, motor commands).
*   **Services**: A request-reply mechanism for nodes to perform synchronous, one-time tasks (e.g., trigger a specific action, query a parameter).
*   **Actions**: A long-running, asynchronous request-reply mechanism for complex tasks that provide continuous feedback and can be preempted (e.g., "drive to goal," "pick up object").
*   **Parameters**: Dynamic configuration values that nodes can expose and modify during runtime.

### Nodes Explanation with Examples

Nodes are the fundamental building blocks of a ROS 2 system. Each node typically encapsulates a single, well-defined function.

**Example**: In an autonomous robot, you might have:
*   A `camer-node` that publishes image data.
*   A `lidar_node` that publishes laser scan data.
*   A `navigation_node` that subscribes to sensor data and publishes velocity commands.
*   A `motor_control_node` that subscribes to velocity commands and sends signals to motors.

### Topics and Messages (Publish-Subscribe)

Topics are the primary means for nodes to exchange data. One node *publishes* messages to a topic, and other nodes *subscribe* to that topic to receive those messages. This is an asynchronous, one-to-many communication model.

**Diagram: Publish-Subscribe Communication**

```
+----------------+       +-----------------+
|   Node A       |       |   Node B        |
| (Publisher)    |       | (Subscriber)    |
+----------------+       +-----------------+
        |                        ^
        | publish                | subscribe
        v                        |
+--------------------------------+
|       /topic_name (message_type)
+--------------------------------+
```

**Examples of Topics and Messages:**

*   `/camera/image` (sensor_msgs/Image): For transmitting camera frames.
*   `/cmd_vel` (geometry_msgs/Twist): For sending linear and angular velocity commands to a robot.
*   `/odom` (nav_msgs/Odometry): For publishing robot's estimated position and orientation.

### Services and Actions

*   **Services**: Used for synchronous, request-reply communication. A client node sends a request to a service server, which processes it and sends back a single response. This is suitable for tasks like querying the robot's current state or triggering a specific, short-duration action.

    **Diagram: Service Communication**

    ```
    +----------------+       +-----------------+
    |   Node A       |       |   Node B        |
    | (Service Client)|----->| (Service Server)|
    +----------------+  Request   +-----------------+
                            <-----
                           Response
    ```

*   **Actions**: Designed for long-running tasks that require continuous feedback and can be preempted. An action client sends a goal to an action server, which executes the task while providing periodic feedback and allowing the client to cancel the goal.

    **Diagram: Action Communication**

    ```
    +----------------+       +-----------------+
    |   Node A       |       |   Node B        |
    | (Action Client)|------>| (Action Server) |
    +----------------+ Goal   +-----------------+
         ^    |
    Feedback|   | Result
         |    v
    +-----------------+
    | (Preempt/Cancel)|
    +-----------------+
    ```

## Practical Examples

### Publisher and Subscriber in Python

First, ensure you have ROS 2 installed and sourced.

**1. Publisher Node (`my_publisher.py`)**

This node will publish a simple "Hello ROS 2" message to a topic every half-second.

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MyPublisher(Node):

    def __init__(self):
        super().__init__('my_publisher_node')
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello ROS 2: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    my_publisher = MyPublisher()
    rclpy.spin(my_publisher)
    my_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**2. Subscriber Node (`my_subscriber.py`)**

This node will subscribe to the "chatter" topic and print received messages.

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MySubscriber(Node):

    def __init__(self):
        super().__init__('my_subscriber_node')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)
    my_subscriber = MySubscriber()
    rclpy.spin(my_subscriber)
    my_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**To run these examples:**

1.  Save the code files in a `ros2_ws/src/my_package` directory.
2.  Create a `setup.py` and `package.xml` for your package (outside the scope of this basic example, but essential for proper ROS 2 package setup).
3.  Build your workspace: `colcon build` (from `ros2_ws`).
4.  Source your workspace: `source install/setup.bash` (Linux/macOS) or `install\setup.bat` (Windows).
5.  Run the nodes in separate terminals:
    ```bash
    ros2 run my_package my_publisher
    ros2 run my_package my_subscriber
    ```

### Command-line Tools for ROS 2

ROS 2 provides a rich set of command-line tools for interacting with and introspecting your robotic system.

| Command                     | Description                                                                     | Example Usage                                    |
| :-------------------------- | :------------------------------------------------------------------------------ | :----------------------------------------------- |
| `ros2 run <pkg_name> <exe_name>` | Executes a node from a specified package.                                       | `ros2 run turtlesim turtlesim_node`              |
| `ros2 node list`            | Lists all active ROS 2 nodes.                                                   | `ros2 node list`                                 |
| `ros2 node info <node_name>` | Displays information about a specific node (topics, services, actions, params). | `ros2 node info /turtlesim`                      |
| `ros2 topic list`           | Lists all active topics.                                                        | `ros2 topic list`                                |
| `ros2 topic info <topic_name>` | Displays information about a topic (type, publishers, subscribers).             | `ros2 topic info /cmd_vel`                       |
| `ros2 topic echo <topic_name>` | Prints messages published on a topic to the console.                            | `ros2 topic echo /odom`                          |
| `ros2 topic pub <topic_name> <msg_type> <args>` | Publishes a message to a topic from the command line.                           | `ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 1.8}}"` |
| `ros2 service list`         | Lists all available services.                                                   | `ros2 service list`                              |
| `ros2 service call <svc_name> <svc_type> <args>` | Calls a service from the command line.                                          | `ros2 service call /clear std_srvs/srv/Empty`    |
| `ros2 param list`           | Lists all parameters available on nodes.                                        | `ros2 param list`                                |
| `ros2 param get <node_name> <param_name>` | Gets the value of a specific parameter.                                         | `ros2 param get /turtlesim background_b`         |
| `ros2 param set <node_name> <param_name> <value>` | Sets the value of a specific parameter.                                         | `ros2 param set /turtlesim background_b 255`     |

## Summary

ROS 2 provides a robust and flexible framework for developing advanced robotic applications. Its decentralized architecture, powered by DDS, offers significant improvements over ROS 1 in areas like real-time performance, security, and multi-robot support. Understanding core concepts such as nodes, topics, services, actions, and parameters is fundamental to building any ROS 2 system. With Python as a popular language for ROS 2 development and a comprehensive suite of command-line tools, developers can efficiently design, implement, and debug complex robotic behaviors.

## Further Reading

*   **Official Documentation**: The most comprehensive resource for learning ROS 2.
    *   [ROS 2 Documentation](https://docs.ros.org/en/foxy/index.html) (adjust distro, e.g., `humble`, `iron`, `jazzy`)
    *   [ROS 2 Tutorials](https://docs.ros.org/en/foxy/Tutorials.html)
*   **Books**:
    *   "Mastering ROS 2" by Ruffin White and Jonathan Cacace
    *   "ROS 2 in 8 Days for Beginners" by Sai Pushpak
*   **Online Courses**:
    *   Various courses on platforms like Coursera, Udemy, and edX covering ROS 2 development.
*   **Community**: Engage with the ROS community for support and knowledge sharing.
    *   [ROS Discourse](https://discourse.ros.org/)
    *   [ROS GitHub](https://github.com/ros2)