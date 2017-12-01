from __future__ import print_function
from PiServerHelper import PiServerHelper
from gattlib import GATTRequester, DiscoveryService
from random import randint
import sys, os
import urllib
import urllib2

import sys, subprocess, time, signal



def destroy():
    print('destroying')



#####################   SETUP   #####################
try:
    service = DiscoveryService("hci0")
    devices = service.discover(4)
    helper = PiServerHelper()
    helper.Setup("Settings.txt", False)
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)


while True:
    addresses = []
    for address, name in list(devices.items()):
        if name[:5] == "Bluno":
            addresses.append(address)
        #print(addresses)
    if addresses:
        try:
            addr = addresses[randint(0, len(addresses)-1)]
            if helper.readable(addr): 
                proc = subprocess.Popen(['python', 'write.py', addr], stdout=subprocess.PIPE)
                output = helper.concatOutput(proc)
                parsed = helper.parseOutput(output)
                #print(output)
                #print(addr)
        
                if parsed != -1:
                    print(addr)
                    print(parsed)
                    helper.insertReading(addr, parsed)
                    
                    if(helper.sendReading()):
                        print("sending reading")

        except KeyboardInterrupt:
            print("stopping cause of keyboard")
            print(helper.readingsToJson())
            time.sleep(1)
            destroy()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)



