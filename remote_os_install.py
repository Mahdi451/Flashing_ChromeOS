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

USER='root'
# CMD='cros flash --log-level info --no-reboot'
CMD='cros flash --log-level info'
CWD=os.getcwd()
GSRC=os.path.expanduser('~/google_source')
IP=str()
IP_LIST=list()
IP_TUP=tuple()

parser=argparse.ArgumentParser()
parser.add_argument('--img',nargs='?',type=str,metavar=('image.bin'),
        default='chromiumos_test_image.bin',help='ChromiumOS test image name')
parser.add_argument('--ip',nargs='?',type=str,metavar=('IP_list.txt'),
        default='ips.txt',help='list of IPs to flash')
args=parser.parse_args()

IMG=('%s/%s' % (CWD,args.img))
TXT=('%s/%s' % (CWD,args.ip))

with open(TXT) as f:
    ip_lines=f.readlines()
    for ip in ip_lines:
        IP_LIST.append(ip.rstrip())
    IP_TUP=IP_LIST


def is_host_live(ip):
    host=ip
    try:
        result=subprocess.call(('ping -c 1 %s;' % host),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    except:
        return False
    if result == 0:
        return True 
    else:
        return False


def remote_os_flash(ip, path):
    flashDict = dict()
    flashing_status = "FAIL"
    IP=ip
    os.chdir(GSRC)
    if is_host_live(IP) == True:  
        input=('%s %s@%s:// %s' % (CMD,USER,IP,IMG))
        p=subprocess.Popen(input,stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,shell=True)
        logging.info("HOST: %s is live." % IP)
        logging.info("Flashing ChromeOS to %s." % IP)
        for line in iter(p.stdout.readline, b''):
            line=bytes.decode(line)
            if ('cros flash completed successfully' or 'Stateful update completed' or 'Update performed successfully') in line.rstrip():
                flashing_status = "PASS"
                flashDict[IP]=flashing_status
                sys.stdout.flush()
                logging.info("\n%s\n"%line.rstrip)
            if ('cros flash failed before completing' or 'Device update failed' or 'Stateful update failed') in line.rstrip():
                flashDict[IP]=flashing_status
                sys.stdout.flush()
                logging.info("\n%s\n"%line.rstrip)
            sys.stdout.flush()
            print("IP: %s   %s" % (ip,line.rstrip()))
        return flashDict
    else:
        logging.info("HOST: %s is not live." % IP)
        flashDict[IP]=flashing_status
        return flashDict
    
        
if __name__ == '__main__': 
    t1=time.perf_counter()
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format,level=logging.INFO,datefmt="%H:%M:%S")
    results = dict()
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        results=pool.map(partial(remote_os_flash,path=IMG), IP_TUP) 
    print ("\n*************************************************************")
    print(results)  
    t2=time.perf_counter()
    tot=t2-t1
    minutes=tot/60
    seconds=tot%60
    print("Execution Time: %dm %ds" % (minutes,seconds))
