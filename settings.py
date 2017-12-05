#!/usr/bin/python3
#   Author: Juan Aznar Poveda
#   Technical University of Cartagena, GIT
#   AGPL License 2017
# Git repo: https://github.com/GITUPCT/CVGIT.git
# -*- coding: utf-8 -*-

from var import *

############################################################################################

## 3) DEFINED FUNCTIONS

###########

def write(value,reg):
    #Write data value in register reg (I2C)
    bus.write_byte_data(address,reg,value)

def status():
    #Read config registers from LMP91000 (I2C)
    STATUS = bus.read_byte_data(address,0)
    LOCK = bus.read_byte_data(address,1)
    TIACN = bus.read_byte_data(address,16)
    REFCN = bus.read_byte_data(address,17)
    MODECN = bus.read_byte_data(address,18)
    print "STATUS : {0:{fill}8b}".format(STATUS, fill='0')
    print "LOCK   : {0:{fill}8b}".format(LOCK, fill='0')
    print "TIACN  : {0:{fill}8b}".format(TIACN, fill='0')
    print "REFCN  : {0:{fill}8b}".format(REFCN, fill='0')
    print "MODECN : {0:{fill}8b}".format(MODECN, fill='0')
    
def readadc():
    #Read ADC161S626 2C Digital Output
    r = spi.readbytes(8)
    bin_r = r
    bin_r[0] = "{0:08b}".format(r[0])
    bin_r[1] = "{0:08b}".format(r[1])
    bin_r[2] = "{0:08b}".format(r[2])
    bin_r = bin_r[0] + bin_r[1] + bin_r[2]
    bin_r = bin_r[2:18]
    if bin_r[0] == '1':
        aux = bin_r.replace('1', '2').replace('0', '1').replace('2', '0')
        adcout = -int(aux,2)-1
    else:
        adcout = int(bin_r,2)
    return adcout

def init(LOCK,TIACN,REFCN,MODECN):
    #Enable TIACN and REFCN writing before use this function, so LOCK first
    #Conversion from binary to hex
    #Configure registers of LMP91000
    #VARIABLES as PARAMETERS
    LOCK = int(LOCK,2)
    TIACN = int(TIACN,2)
    REFCN = int(REFCN,2)
    MODECN = int(MODECN,2)
    write(LOCK,1)
    write(TIACN,16)
    write(REFCN,17)
    write(MODECN,18)
    
def step(REFCN):
    #Enable TIACN and REFCN writing before use this function, so LOCK first
    #Conversion from binary to hex
    #Configure registers of LMP91000, simple function for loops
    #VARIABLES as PARAMETERS
    REFCN = int(REFCN,2)
    write(REFCN,17)


############################################################################################







