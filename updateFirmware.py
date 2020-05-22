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
import os
import sys

# TODO: mejorar subprocess.call para exportar salida en file_handler (solo se printea)

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

file_handler = logging.FileHandler("upgradeFW.log")
file_handler.setFormatter(formatter2)
logger.addHandler(file_handler)

##################################################################################################################
#                                                    Methods                                                     #
##################################################################################################################

def findATPort():
    ports = serial.tools.list_ports.comports()
    atPort = None
    for port, desc, _ in sorted(ports):
        if "AT" in desc:
            atPort = port
            break
    return atPort

def getFWVersion(atPort):
    filteredResponse = None
    try:
        logger.debug("Connecting serial...")
        ser = serial.Serial(port=atPort, baudrate=115200, timeout=1)
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

def initBootloader(atPort):
    success = False
    try:
        logger.debug("Connecting serial...")
        ser = serial.Serial(port=atPort, baudrate=115200, timeout=1)
        time.sleep(0.3)
        ser.reset_input_buffer()
        ser.write(b'AT+BOOTLDR\r\n')
        time.sleep(3)
        ser.close()
        success = True
    except Exception as ex:
        logger.exception(ex)
    return success

def upgradeFirmware(ans, atPort):
    if ans == "Y":
        logger.info("Actualizando FW...")
        bootloaderOk = initBootloader(atPort)
        if bootloaderOk:
            logger.info("----------------------------------- Fastboot Mode ---------------------------------------")
            subprocess.call("fastboot devices")
            subprocess.call("fastboot flash aboot appsboot.mbn")
            subprocess.call("fastboot flash rpm rpm.mbn")
            subprocess.call("fastboot flash sbl sbl1.mbn")
            subprocess.call("fastboot flash tz tz.mbn")
            subprocess.call("fastboot flash modem modem.img")
            subprocess.call("fastboot flash boot boot.img")
            subprocess.call("fastboot flash system system.img")
            subprocess.call("fastboot flash recovery recovery.img")
            subprocess.call("fastboot flash recoveryfs recoveryfs.img")
            subprocess.call("fastboot reboot")


def main():
    logging.info("Iniciando programa de actualizacion de firmware modulo Sim7600")
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
            sys.exit()

    logger.info(f"Firmware a instalar: {newFWVersion}")
    time.sleep(2)
    for i in range(3):
        logger.info("Buscando puertos...")
        atPort = findATPort()
        if not atPort:
            logger.error(f"Puerto no encontrado. Revisa la conexión y presiona enter para intentar [{i+1}/3]")
            input()
        else:
            break
    if not atPort:
        logger.error("Puerto no encontrado")
    else:
        logger.info(f"SIM7600 encontrado en {atPort}")
        logger.info("Revisando version de FW actual...")
        actualFWVersion = getFWVersion(atPort)
        logger.info(f"   Version = {actualFWVersion}")
        if newFWVersion != actualFWVersion:
            logger.info("Actualizacion disponible! Deseas instalar? [Y/N] ")
            ans = input("-------> ")
            upgradeFirmware(ans, atPort)
        else:
            logger.info("Ya tienes esta version instalada! Deseas reinstalar?? [Y/N] ")
            ans = input("-------> ")
            upgradeFirmware(ans, atPort)

    logger.info("Programa finalizado!")

if __name__ == "__main__":
    main()
