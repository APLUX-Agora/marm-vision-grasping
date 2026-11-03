#!/usr/bin/env python3
"""Read-only platform checks for the MARM software-only test."""
import argparse,os,platform,shutil,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--soc',required=True);p.add_argument('--ubuntu',required=True);args=p.parse_args()
failed=False

def check(name,ok,detail):
 global failed
 print(('CHECKED' if ok else 'FAILED')+' '+name+': '+detail);failed|=not ok
os_release=platform.freedesktop_os_release()
check('target',args.soc=='QCS8550','expected QCS8550; selected '+args.soc)
check('architecture',platform.machine() in ('aarch64','arm64'),'expected ARM64; detected '+platform.machine())
check('system',os_release.get('ID')=='ubuntu' and os_release.get('VERSION_ID')==args.ubuntu=='22.04','expected Ubuntu 22.04; detected '+os_release.get('PRETTY_NAME','unknown'))
raw=os.environ.get('AGORA_WORKSPACE','')
check('workspace',bool(raw) and Path(raw).is_absolute(),'set AGORA_WORKSPACE to an absolute writable path')
if raw and Path(raw).is_absolute():
 try:
  path=Path(raw);path.mkdir(parents=True,exist_ok=True)
  check('workspace access',os.access(path,os.W_OK),str(path))
  check('disk space',shutil.disk_usage(path).free>=4*1024**3,'at least 4 GiB free required')
 except OSError as exc:check('workspace access',False,str(exc))
check('git',bool(shutil.which('git')),'available' if shutil.which('git') else 'install before step 2: sudo apt-get install -y git')
# Read-only checks: do not configure packages or run automatic system repair.
try:
 audit=subprocess.run(['dpkg','--audit'],capture_output=True,text=True,timeout=30,env={**os.environ,'LC_ALL':'C'})
 healthy=audit.returncode==0 and not audit.stdout.strip()
 check('package transactions',healthy,'no unfinished dpkg transactions' if healthy else 'unfinished package transactions; ask the cloud administrator to restore package health')
 dependencies=subprocess.run(['apt-get','-s','check'],capture_output=True,text=True,timeout=30,env={**os.environ,'LC_ALL':'C'})
 check('APT dependencies',dependencies.returncode==0,'consistent' if dependencies.returncode==0 else 'inconsistent; ask the cloud administrator before installing dependencies')
except (OSError,subprocess.TimeoutExpired) as exc:
 check('package health',False,str(exc))
for name,ok in [('ROS 2 Humble',Path('/opt/ros/humble/setup.bash').is_file()),('colcon',bool(shutil.which('colcon')))]:
 print(('CHECKED' if ok else 'NEEDS_SETUP')+' '+name+(': available' if ok else ': install in step 3'))
print('FAILED: fix platform/workspace checks before continuing.' if failed else 'CHECKED: platform ready; resolve NEEDS_SETUP items in step 3.')
sys.exit(1 if failed else 0)
