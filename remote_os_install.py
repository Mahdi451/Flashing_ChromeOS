""" 
options: [--img testimage.bin] [--ip iplist.txt] 
example: python remote_os_install.py --img chromiumos_test_image.bin --ip ips.txt
## python script, iplist.txt, and image.bin must be in same folder ##
"""

import os, sys, logging
import argparse, subprocess
import multiprocessing, time
from functools import partial
from collections import defaultdict

user='root'
# command='cros flash --log-level info --no-reboot'
command='cros flash --log-level info'
curr_dir=os.getcwd()
google_src=os.path.expanduser('~/google_source')
list_ip=list()
tuple_ip=tuple()

parser=argparse.ArgumentParser()
parser.add_argument('--image',nargs='?',type=str,metavar=('image.bin'),
        default='chromiumos_test_image.bin',help='ChromiumOS test image name')
parser.add_argument('--ip',nargs='?',type=str,metavar=('IP_list.txt'),
        default='IPs.txt',help='list of IPs to flash')
args=parser.parse_args()

img_path=('%s/%s' % (curr_dir,args.img))
ip_txt=('%s/%s' % (curr_dir,args.ip))

with open(ip_txt) as f:
    ip_lines=f.readlines()
    for ip in ip_lines:
        list_ip.append(ip.rstrip())
    tuple_ip=list_ip


def is_host_live(dut_ip):
    try:
        result=subprocess.call(('ping -c 1 %s;' % dut_ip),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    except:
        return False
    if result == 0:
        return True 
    else:
        return False


def remote_os_flash(dut_ip, path):
    flashDict = dict()
    flashing_status = "FAIL"
    os.chdir(google_src)
    if is_host_live(dut_ip) == True:  
        input=('%s %s@%s:// %s' % (command,user,dut_ip,img_path))
        p=subprocess.Popen(input,stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,shell=True)
        logging.info("HOST: %s is live." % dut_ip)
        logging.info("Flashing ChromeOS to %s." % dut_ip)
        for line in iter(p.stdout.readline, b''):
            line=bytes.decode(line)
            print("IP: %s    %s" % (ip,line.rstrip()))
            if ('cros flash completed successfully' or 'Stateful update completed' or 'Update performed successfully') in line.rstrip():
                flashing_status = "PASS"
                flashDict[dut_ip]=flashing_status
                return flashDict
            elif ('cros flash failed before completing' or 'Device update failed' or 'Stateful update failed') in line.rstrip():
                flashDict[dut_ip]=flashing_status
                return flashDict
        flashDict[dut_ip]=flashing_status
        return flashDict
    else:
        logging.info("HOST: %s is not live." % dut_ip)
        flashDict[dut_ip]=flashing_status
        return flashDict
    
        
if __name__ == '__main__': 
    t1=time.perf_counter()
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format,level=logging.INFO,datefmt="%H:%M:%S")
    results = dict()
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        results=pool.map(partial(remote_os_flash,path=img_path), tuple_ip) 
    print ("\n*************************************************************")
    print(results)  
    t2=time.perf_counter()
    tot=t2-t1
    minutes=tot/60
    seconds=tot%60
    print("Execution Time: %dm %ds" % (minutes,seconds))
