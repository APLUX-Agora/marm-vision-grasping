#!/usr/bin/env python3
"""Exercise the real ROS RGB node with synthetic input; no camera or actuators."""
import argparse,json,math,os,secrets,signal,subprocess,sys,time
from pathlib import Path
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image,CompressedImage
from std_msgs.msg import String
from geometry_msgs.msg import TransformStamped,PoseStamped
from tf2_ros import StaticTransformBroadcaster

p=argparse.ArgumentParser();p.add_argument('--resources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--timeout',type=float,default=30);args=p.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
for name in ('result.json','result.jpg'):(args.output/name).unlink(missing_ok=True)
calibration=(args.resources/'camera.yaml').resolve()
if not calibration.is_file():sys.exit('FAILED: missing camera.yaml; complete step 4 first.')
env=dict(os.environ,ROS_LOCALHOST_ONLY='1',ROS_DOMAIN_ID='87',ROS_LOG_DIR=str(args.output.resolve()/'ros-logs'))
# All ROS topics stay in a private namespace and local-only DDS domain.
os.environ.update({k:env[k] for k in ('ROS_LOCALHOST_ONLY','ROS_DOMAIN_ID','ROS_LOG_DIR')})
namespace='/agora_marm_test_'+secrets.token_hex(4)
proc=None;node=None;passed=False
try:
 rclpy.init(args=['--ros-args','-r','/tf_static:='+namespace+'/tf_static']);node=Node('software_test',namespace=namespace)
 seen={'color':False,'pose':False,'image':False};sample={};latest=[None]
 def color(msg):seen['color']=msg.data=='r'
 def pose(msg):
  xyz=[msg.pose.position.x,msg.pose.position.y,msg.pose.position.z]
  if msg.header.frame_id=='1' and all(math.isfinite(x) for x in xyz) and abs(xyz[0]-.2)<.01 and abs(xyz[1])<.01 and abs(xyz[2])<.01:
   seen['pose']=True;sample['object_pose_m']=xyz
 def image(msg):
  decoded=cv2.imdecode(np.frombuffer(msg.data,dtype=np.uint8),cv2.IMREAD_COLOR)
  if decoded is not None:seen['image']=True;latest[0]=decoded
 subs=[node.create_subscription(String,'rgb_detection/color_type',color,10),node.create_subscription(PoseStamped,'object_pose',pose,10),node.create_subscription(CompressedImage,'rgb_detection/compressed',image,10)]
 pub=node.create_publisher(Image,'camera/image_rect',10)
 broadcaster=StaticTransformBroadcaster(node)
 transform=TransformStamped();transform.header.frame_id='base_footprint';transform.child_frame_id='agora_test_camera';transform.header.stamp=node.get_clock().now().to_msg()
 # Known test transform puts the target inside the upstream pose publication bounds.
 transform.transform.translation.x=.2;transform.transform.translation.z=-.2;transform.transform.rotation.w=1.;broadcaster.sendTransform(transform)
 fixture=np.zeros((480,640,3),np.uint8);cv2.circle(fixture,(320,240),40,(0,0,255),-1)
 cv2.imwrite(str(args.output/'input.png'),fixture)
 log=(args.output/'node.log').open('w')
 proc=subprocess.Popen(['ros2','run','capture_image','rgb_detect_pose_node','--ros-args','-r','__ns:='+namespace,'-r','/tf:='+namespace+'/tf','-r','/tf_static:='+namespace+'/tf_static','-r','/camera/image_rect:='+namespace+'/camera/image_rect','-r','/rgb_detection/color_type:='+namespace+'/rgb_detection/color_type','-r','/rgb_detection/compressed:='+namespace+'/rgb_detection/compressed','-p','show_gui:=false','-p','camera_frame:=agora_test_camera','-p','camera_calibration_file:='+str(calibration),'-p','color_thresholds_file:='+str((args.output/'unused-thresholds.yaml').resolve())],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 deadline=time.monotonic()+args.timeout;next_publish=0.0
 while time.monotonic()<deadline and not all(seen.values()):
  if proc.poll() is not None:raise RuntimeError('RGB node exited; inspect node.log')
  if time.monotonic()>=next_publish:
   msg=Image();msg.header.frame_id='agora_test_camera';msg.header.stamp=node.get_clock().now().to_msg();msg.height=480;msg.width=640;msg.encoding='bgr8';msg.step=640*3;msg.data=fixture.tobytes();pub.publish(msg)
   next_publish=time.monotonic()+.1
  rclpy.spin_once(node,timeout_sec=.05)
 for name,ok in seen.items():print(('CHECKED' if ok else 'FAILED')+' '+name)
 if not all(seen.values()):raise RuntimeError('Timed out waiting for actual node outputs; inspect node.log')
 if not cv2.imwrite(str(args.output/'result.jpg'),latest[0]):raise RuntimeError('Could not write result.jpg')
 sample.update(status='COMPLETED',scope='software_only',checks=seen,physical_calibration=False,physical_motion=False)
 (args.output/'result.json').write_text(json.dumps(sample,indent=2)+'\n');print('COMPLETED: '+str(args.output/'result.json'));passed=True
except Exception as exc:print('FAILED: '+str(exc),file=sys.stderr)
finally:
 if proc is not None and proc.poll() is None:
  os.killpg(proc.pid,signal.SIGINT)
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
 if node is not None:node.destroy_node()
 if rclpy.ok():rclpy.shutdown()
sys.exit(0 if passed else 1)
