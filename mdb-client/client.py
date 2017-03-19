from pylibftdi import SerialDevice
from pylibftdi import Driver
import subprocess
import os
import time

subprocess.call(['sudo', 'kextunload', '-b', 'com.apple.driver.AppleUSBFTDI'])

def get_ftdi_device_list():
    """
    return a list of lines, each a colon-separated
    vendor:product:serial summary of detected devices
    """
    dev_list = []
    for device in Driver().list_devices():
        # list_devices returns bytes rather than strings
        dev_info = map(lambda x: x.decode('latin1'), device)
        # device must always be this triple
        vendor, product, serial = dev_info
        dev_list.append("%s:%s:%s" % (vendor, product, serial))
    return dev_list

print get_ftdi_device_list()

# with SerialDevice(mode='t') as dev:
#     dev.baudrate = 115200
#     print dev
#     while (True):
#         dev.dtr = 0
#         time.sleep(.5)
#         dev.dtr = 1
#         time.sleep(.5)
#         print 'cycle'

# import usb.core
# import usb.util

# # find our device
# dev = usb.core.find(idVendor=0x0403, idProduct=0x6010)

# # was it found?
# if dev is None:
#     raise ValueError('Device not found')

