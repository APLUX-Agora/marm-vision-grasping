# MARM task guide

## Software validation

Agora keeps its three software steps: select content, select compute hardware and
system, then deploy and validate. The remaining task sections are documents guiding the user through local
hardware assembly, wiring, bring-up and calibration. Cloud devices validate software only. Choose a validation method based on the peripherals actually connected.

The prototype targets QCS8550 / Ubuntu 22.04. On-device adaptation is pending.
This revision provides the task structure and source reference. It does not supply
a newly qualified one-command deployment, recorded-input adapter or simulator.

## Assemble and connect, step by step

1. Compare the parts with the mechanical files in `models/`, then secure the base
   to the workbench.
2. Install joint servos and links in the order shown by the mechanical design.
   Record each controller channel and its matching joint.
3. Install the gripper and camera bracket. Record whether the camera is mounted
   on the arm (Eye-in-Hand) or outside it (Eye-on-Base).
4. With power off, connect servos and their specified supply according to the
   controller pinout. Confirm supply ratings and grounding.
5. Connect the camera to QCS8550 over USB, and connect the servo controller to the
   host through USB-to-serial.
6. Identify the device paths below, then continue with local component bring-up
   and calibration. No cloud terminal command assembles or connects this hardware.

## Identify connected devices

Run on the local host with the camera and servo controller connected:

```bash
lsusb
ls -l /dev/video* /dev/serial/by-id/
```

Expected: the camera and serial controller are enumerated. Record actual device
paths and check account permissions before putting the paths in project settings.
A missing device is a connection/driver prerequisite to resolve first.

## Bring-up and calibration

| Order | Action | Expected result / saved artifact |
| --- | --- | --- |
| 1 | Check assembly, power and wiring | Correct joint numbering, supply ratings and controller pinout |
| 2 | Verify camera and serial device access | Stable image and accessible controller path |
| 3 | Test each component separately | Correct low-speed joint direction and independent gripper control |
| 4 | Calibrate joint zero offsets | Joint offset configuration for this assembly |
| 5 | Calibrate camera intrinsics | Camera parameter file matching the camera and resolution |
| 6 | Calibrate hand-eye transform | Correct Eye-in-Hand/Eye-on-Base configuration and saved transform |
| 7 | Run the complete grasping loop | Consistent perception, coordinates, planned motion, grasp and placement |

Use the actual checkerboard geometry and camera mounting. Reconfirm calibration
when the relevant hardware, resolution or installation changes. Physical execution
requires an assembled robot; verify planned movement before commanding actuators.

## Status in the task

Preparation and bring-up checkboxes are the user's own records. They do not trigger
commands, move hardware, or certify that the platform automatically tested a device.
Each task stores its own confirmations independently.
