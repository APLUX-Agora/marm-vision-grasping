# MARM Vision Grasping · Agora

A desktop robot-arm reference project combining ROS 2, OpenCV perception, MoveIt 2
motion planning, and serial servo control. This public Agora copy preserves the
history and source of [APLUX-Official/marm_A1](https://github.com/APLUX-Official/marm_A1).

## What is included

- `A1_description` / `A1_moveit_config`: robot description and planning configuration.
- `arm_controller`: serial servo control and joint offset configuration.
- `capture_image`: RGB color and ArUco perception nodes.
- `custom_interface`: ROS 2 service/action interfaces.
- `moveit_controller_server`: motion-control examples.
- `models`: mechanical model files.

Reference software: Ubuntu 22.04, ROS 2 Humble, MoveIt 2, OpenCV, tf2 and the
project's calibration tools. The Agora catalog uses QCS6490 as its reference
compute platform. This copy does not constitute a new BSP or hardware qualification.

## Hardware preparation

| Part | Reference | Quantity |
| --- | --- | --- |
| Robot arm | A1 desktop six-axis structure and gripper | 1 |
| Actuators | MG996R servos, matching the assembly | 6 |
| Servo controller | Matching serial protocol and servo interfaces | 1 |
| Compute platform | Project-compatible host / development board | 1 |
| Camera | Compatible RGB USB camera | 1 |
| Calibration target | ArUco or checkerboard with measured dimensions | 1 |
| Power and cables | Follow actual hardware ratings and pinout | As needed |

Connect the camera to the host over USB. Connect the servo controller through
USB-to-serial, then connect the servos according to that controller's pinout.
Power the actuators using the specified supply, not directly from the host's USB
port. Confirm grounding and interface definitions against the actual hardware.

## Get the source

```bash
git clone https://github.com/APLUX-Agora/marm-vision-grasping.git
```

Use the ROS 2 workspace convention and resolve the dependencies declared in the
packages before building. `easy_handeye2` is an external prerequisite: it is not
included as an active package in this upstream revision. Do not treat the editor
history under `.history` as an installed dependency.

## Reproduction order

1. Check assembly, power, joint numbering and connections.
2. Identify the camera and serial controller on the local host.
3. Bring up the camera and controller separately; check joint directions at low speed.
4. Calibrate joint zero offsets, camera intrinsics, then the hand-eye transform.
5. Check perception, coordinate transforms and planned trajectories before executing grasping.
6. Verify grasp, placement and return-to-home on the actual assembly.

See [the Agora task guide](docs/AGORA_TASK_GUIDE.md) for scope and expected results.
The supplied calibration files are examples for a specific assembly, not reusable
calibration for every device. Keep the motion area clear during physical tests.

## Agora validation boundary

The task combines software validation, hardware preparation, connection notes and
calibration guidance. Software running on a board does not establish that camera
calibration or physical grasping has been validated. The current Agora cloud pool
has QCS8550 compute boards, without a connected MARM arm or project camera.
This repository has not been qualified for complete cloud robot reproduction.

## Provenance and notices

Copied from upstream revision `dc22a18a32992afe53475af9b33d813c8f6f9d1a`.
Original source and package notices are retained; see [NOTICE.md](NOTICE.md).
New Agora documentation is in English. No original upstream repository was changed.
