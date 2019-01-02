#!/usr/bin/env python
#
# author: Orestis Evangelatos, orestevangel@gmail.com
#
# Notes:
# pexpect uses regular expression so characters that have special meaning
# in regular expressions, e.g. [ and ] must be escaped with a backslash.
#
#   Copyright 2016 Orestis Evangelatos
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import pexpect
import sys
import time
from sensor_calcs import *
import json
import select
from Sensortag_classes import *
import requests
import warnings
import datetime
import traceback
import httplib
import math
    
def hexTemp2C(raw_temperature):
	
	string_temp = raw_temperature[0:2]+' '+raw_temperature[2:4]+' '+raw_temperature[4:6]+' '+raw_temperature[6:8] #add spaces to string	
	#TODO:Fix the following line so that I don't have to add and to remove spaces
	raw_temp_bytes = string_temp.split() # Split into individual bytes
	raw_ambient_temp = int( '0x'+ raw_temp_bytes[3]+ raw_temp_bytes[2], 16) # Choose ambient temperature (reverse bytes for little endian)
	raw_IR_temp = int('0x' + raw_temp_bytes[1] + raw_temp_bytes[0], 16)
	IR_temp_int = raw_IR_temp >> 2 & 0x3FFF
	ambient_temp_int = raw_ambient_temp >> 2 & 0x3FFF # Shift right, based on from TI
	ambient_temp_celsius = float(ambient_temp_int) * 0.03125 # Convert to Celsius based on info from TI
	IR_temp_celsius = float(IR_temp_int)*0.03125
	ambient_temp_fahrenheit = (ambient_temp_celsius * 1.8) + 32 # Convert to Fahrenheit
	
	print "INFO: IR Celsius:    %f" % IR_temp_celsius
	print "INFO: Ambient Celsius:    %f" % ambient_temp_celsius
	#print "Fahrenheit: %f" % ambient_temp_fahrenheit		
	return (IR_temp_celsius, ambient_temp_celsius)
	
	
	
def hexLum2Lux(raw_luminance):
	
	m ="0FFF"
	e ="F000" 
	raw_luminance = int(raw_luminance,16)
	m = int(m, 16) #Assign initial values as per the CC2650 Optical Sensor Dataset
	exp = int(e, 16) #Assign initial values as per the CC2650 Optical Sensor Dataset	
	m = (raw_luminance & m) 		#as per the CC2650 Optical Sensor Dataset
	exp = (raw_luminance & exp) >> 12 	#as per the CC2650 Optical Sensor Dataset
	luminance = (m*0.01*pow(2.0,exp)) 	#as per the CC2650 Optical Sensor Dataset	
	return luminance #returning luminance in lux

def hexHum2RelHum(raw_humidity):

    humidity = float((int(raw_humidity,16)))/65536*100 #get the int value from hex and divide as per Dataset.    
    return humidity
    
    
    
def hexPress2Press(raw_pressure):

    pressure = int(raw_pressure,16)
    pressure = float(pressure)/100.0    
    return pressure  

def main():
    global datalog
    global barometer
    
    bluetooth_adr = sys.argv[1]
    
    #print ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))   
    print "INFO: starting.."

    tag  = SensorTag(bluetooth_adr) #pass the Bluetooth Address
    
    """GETTING THE IR AND AMBIENT TEMPERATURE"""
    tag.char_write_cmd(0x24,01) #Enable temperature sensor
	IR_temp_celsius, Ambient_temp_celsius = hexTemp2C(tag.char_read_hnd(0x21, "temperature")) #get the hex value and parse it to get Celcius
		
    """GETTING THE LUMINANCE"""
    tag.char_write_cmd(0x44,01)
    lux_luminance = hexLum2Lux(tag.char_read_hnd(0x41, "luminance"))	    
      
    """GETTING THE HUMIDITY"""
    tag.char_write_cmd(0x2C,01)
    rel_humidity = hexHum2RelHum(tag.char_read_hnd(0x29, "humidity"))	
	
    """GETTING THE Barometric Pressure"""
    tag.char_write_cmd(0x34,01)
    barPressure = hexPress2Press(tag.char_read_hnd(0x31, "barPressure"))
    
    #tag.notification_loop()
    
if __name__ == "__main__":
    main()

