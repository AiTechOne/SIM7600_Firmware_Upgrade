#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "Felipe Tejada"
__credits__ = "Felipe Tejada"
__version__ = 1.0
__maintainer__ = "Felipe Tejada"
__email__ = "felipe@pm.me"
__status__ = "dev"

import serial.tools.list_ports
import logging
import subprocess
import serial
import time
import os.path
import os
import platform

##################################################################################################################
#                                                 logger init                                                    #
##################################################################################################################

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('Upgrade Tool -> %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
formatter2 = logging.Formatter('Upgrade Tool ->%(asctime)s(%(lineno)d-%(levelname)s): %(message)s')

file_handler = logging.FileHandler("log.log")
file_handler.setFormatter(formatter2)
logger.addHandler(file_handler)

##################################################################################################################
#                                                    Methods                                                     #
##################################################################################################################

def find_at_port():
    at_port = None
    if platform.system() == 'Linux':
        if os.path.exists('/dev/SimAT'):
            return '/dev/SimAT'
    elif platform.system() == 'Windows':
        ports = serial.tools.list_ports.comports()
        at_port = None
        for port, desc, _ in sorted(ports):
            if "AT" in desc:
                at_port = port
                break
    else:
        logger.error("OS not 'supported' (check code and try manually)")
    return at_port

def get_current_fw_version(at_port):
    filteredResponse = None
    try:
        logger.debug("Connecting serial...")
        ser = serial.Serial(port=at_port, baudrate=115200, timeout=1)
        time.sleep(0.3)
        ser.reset_input_buffer()
        ser.write(b'AT+CGMR\r\n')
        time.sleep(0.1)
        atResponse = ser.read(1)
        time.sleep(0.1)
        data_left = ser.inWaiting()
        atResponse += ser.read(data_left)
        filteredResponse = atResponse.decode('utf-8')
        filteredResponse = filteredResponse.split()[2]
        ser.close()
    except Exception as ex:
        logger.exception(ex)
    return filteredResponse

def init_bootloader_mode(at_port):
    success = False
    try:
        logger.debug("Connecting serial...")
        ser = serial.Serial(port=at_port, baudrate=115200, timeout=1)
        time.sleep(0.3)
        ser.reset_input_buffer()
        ser.write(b'AT+BOOTLDR\r\n')
        time.sleep(3)
        ser.close()
        success = True
    except Exception as ex:
        logger.exception(ex)
    return success

def upgrade_firmware(ans, at_port):
    if ans == "Y":
        logger.info("Upgrading Firmware...")
        bootloaderOk = init_bootloader_mode(at_port)
        if bootloaderOk:
            logger.info("----------------------------------- Fastboot Mode ---------------------------------------")
            subprocess.call("fastboot devices".split())
            subprocess.call("fastboot flash aboot appsboot.mbn".split())
            subprocess.call("fastboot flash rpm rpm.mbn".split())
            subprocess.call("fastboot flash sbl sbl1.mbn".split())
            subprocess.call("fastboot flash tz tz.mbn".split())
            subprocess.call("fastboot flash modem modem.img".split())
            subprocess.call("fastboot flash boot boot.img".split())
            subprocess.call("fastboot flash system system.img".split())
            subprocess.call("fastboot flash recovery recovery.img".split())
            subprocess.call("fastboot flash recoveryfs recoveryfs.img".split())
            subprocess.call("fastboot reboot".split())


def main():
    logging.info("############# Initializing ################")
    fw_available = [fw for fw in os.listdir() if "LE" in fw]
    if len(fw_available) == 1:
        newFWVersion = fw_available[0]
    else:
        logger.info("More than one firmware folder available!")
        for k,fw in enumerate(fw_available):
            logger.info(f"\t{k+1}. {fw}")
        fw_index = input("Please choose index of Firmware to be installed: ")
        try:
            newFWVersion = fw_available[int(fw_index)-1]
            os.chdir(newFWVersion)
        except Exception:
            logger.info("Wrong index. It's not that hard... Exiting!")
            return False

    logger.info(f"Firmware to be installed: {newFWVersion}")
    time.sleep(2)
    for i in range(3):
        logger.info("Searching AT Port...")
        at_port = find_at_port()
        if not at_port:
            logger.error(f"Port not found. Check USB connection and press enter to retry [{i+1}/3]")
            input()
        else:
            break
    if not at_port:
        logger.error("Port not found")
    else:
        logger.info(f"SIM7600 AT Port found: {at_port}")
        logger.info("Checking current FW Version...")
        actualFWVersion = get_current_fw_version(at_port)
        logger.info(f"   Current Version = {actualFWVersion}")
        if newFWVersion != actualFWVersion:
            logger.info("Upgrade available! Go? [Y/N] ")
            ans = input("-------> ")
            upgrade_firmware(ans, at_port)
        else:
            logger.info("Already you have that FW version installed! Do you want to reinstall?? [Y/N] ")
            ans = input("-------> ")
            upgrade_firmware(ans, at_port)

    logger.info("Program finished!")

if __name__ == "__main__":
    main()
