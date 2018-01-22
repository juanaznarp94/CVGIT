#!/usr/bin/python3
#   Author: Juan Aznar Poveda
#   Technical University of Cartagena, GIT
#   Copyright (C) 2017
# Git repo: https://juanaznarp94@bitbucket.org/juanaznarp94/tfm.git
# -*- coding: utf-8 -*-

############################################################################################

from var import *
from settings import *
import matplotlib, sys
import time
import math
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from numpy import arange, sin, pi
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from Tkinter import *
from ttk import *
import pylab
import csv
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT) 
GPIO.setup(13, GPIO.OUT)

root = Tk()
root.wm_title("CVGIT 2017 (C)")
root.geometry('1280x800+100+100')
root.style = Style()
#('clam', 'alt', 'default', 'classic')

root.style.theme_use('clam')

GPIO.output(11,False) ## RED
GPIO.output(13,True) ## GREEN

w = Text(root, width='50', height='12', bg='white', relief = 'groove')
results = Text(root, width='50', height='2', bg='white', relief = 'groove')
#w.grid(column='0',row='12',columnspan='1',rowspan='1')
#results.grid(column='0',row='11',columnspan='1',rowspan='1')
w.grid(column='1',row='12',columnspan='2',rowspan='1')
results.grid(column='1',row='11',columnspan='2',rowspan='1')

w.insert('1.0', 'Welcome to Ciclic Voltammetry Client \n Interface. Please:\n 1) Insert sensor in its adapters plug.\n 2) Choose your fit config\n    (TIA and OPMODE).\n 3) Click Start and save graph.\n'+'\n'+'\n'+'Technical University of Cartagena'+'\n'+ 'TIC GIT 2017 '+u"\u00A9")
#results.insert('1.0', 'Determined concentration results\n(mg and M)')

GRAPH_title = Label(root, text='Edit graph title')
k = Entry(root,width='40')
k.grid(column='1',row='10',columnspan='2',rowspan='1')
GRAPH_title.grid(column='1',row='9',columnspan='2',rowspan='1')

volume = Label(root, text='Input volume')
v = Entry(root,width='40')
v.grid(column='1',row='12',columnspan='2',rowspan='1')
volume.grid(column='1',row='11',columnspan='2',rowspan='1')

TIA_dicc = {'Default':TIACN_TIAG_DEFAULT_RLOAD_010,
            '2.75 KOhms':TIACN_TIAG_2_75_RLOAD_010,
            '3.5 KOhms':TIACN_TIAG_3_50_RLOAD_010,
            "7 KOhms":TIACN_TIAG_7_00_RLOAD_010,
            "14 KOhms":TIACN_TIAG_14_0_RLOAD_010,
            "35 KOhms":TIACN_TIAG_35_0_RLOAD_010,
            "120 KOhms":TIACN_TIAG_120__RLOAD_010,
            "350 KOhms":TIACN_TIAG_350__RLOAD_010}

TIA_values = {'Default':0,
            '2.75 KOhms':2750,
            '3.5 KOhms':3500,
            "7 KOhms":7000,
            "14 KOhms":14000,
            "35 KOhms":35000,
            "120 KOhms":120000,
            "350 KOhms":350000}

OPMODE_dicc = {"Deep Sleep":MODECN_OP_MODE_DEEPSLEEP,
               "2-Lead GRGC":MODECN_OP_MODE_2LEADGNDC,
               "Standby":MODECN_OP_MODE_STANDBY00,
               "3-Lead AC":MODECN_OP_MODE_3LEADAMPC,
               "Temperature MT-OFF":MODECN_OP_MODE_TEMPMEAOF,
               "Temperature MT-ON":MODECN_OP_MODE_TEMPMEAON}

############################################################################################
##  PLOT CONFIG AND SWEEP MAIN FUNCTION

f = Figure(figsize=(5,4), dpi=120, facecolor='white', frameon=False,tight_layout=True)
a = f.add_subplot(111,title='CV 50mV/s - CVGIT',
                  xlabel='Applied voltage (V)',
                  ylabel='Registered current ('+ u"\u00B5"+'A)',autoscale_on=True)

##t = SW_BIAS_N + SW_BIAS_P + SW_BIAS_P[::-1] + SW_BIAS_N[::-1]
t = SW_BIAS_P_TOTAL
data = [0]*len(t)
DATA = data
a.plot(t,data,'darkblue')
dataPlot = FigureCanvasTkAgg(f, master=root)
dataPlot.show()
dataPlot.get_tk_widget().grid(column='5',row='3', columnspan='2', rowspan='10')


def on_change(k):
    f = Figure(figsize=(5,4), dpi=120, facecolor='white', frameon=False,tight_layout=True)
    a = f.add_subplot(111,title=k.get(),
    xlabel='Applied voltage (V)',
    ylabel='Registered current ('+ u"\u00B5"+'A)',autoscale_on=True)

def update(data):
    a.cla()
    a.set_xlabel('Applied voltage (V)')
    a.set_ylabel('Registered current ('+ u"\u00B5"+'A)')
    a.set_title(k.get())
    a.plot(t,data,'darkblue')
    dataPlot.show()

def printdout(num):
    TIAG = TIA_values["{}".format(variable_TIA.get())]
    value = readadc()
    vref = 2.5
    vmax = 5-(vref/(2**16))
    N = 16
    binmax = ((2**N)-1)
    volts = (vmax*value)/(binmax)+vref
    current = ((volts-(vref/2))/(TIAG))*1000000
    print ">> Step: %5.3f\n >> Voltage: %5.3f V\m >> Current: %5.3f uA" %(num,volts,current)
    return [current, ">> Step: %5.3f\n >> Voltage: %5.3f V\m >> Current: %5.3f uA" %(num,volts,current)]
    
def sweep(TIA,OPMODE):
    #SWEEP_1 (-0.6 to 0.6, 50mV/s)
    #init(LOCK,TIACN,REFCNinit,MODECN)
    #step(REFCN)
    init(LOCKWR,\
        TIA,\
        REFCN_BIAS_N[0],\
        OPMODE)
    #BOTTOMUP:
    ##TIME CONTROL
##    for n in range(len(REFCN_BIAS_N)):
##        step(REFCN_BIAS_N[-1-n])
##        #start_time = time.time()
##        status()
##        time.sleep(0.1615)
##        aux = printdout(SW_BIAS_N[n])
##        DATA[n] = aux[0]
##        string = aux[1]
##        w.insert('1.0', string +'\n'+'\n')
##        update(DATA)
        #print("--- %s seconds ---" % (time.time() - start_time))
    for p in range(len(REFCN_BIAS_P_TOTAL)):
        step(REFCN_BIAS_P_TOTAL[p])
        status()
        time.sleep(0.1615)
        aux = printdout(SW_BIAS_P_TOTAL[p])
        DATA[p] = aux[0]
        #DATA[cn+p-1] = aux[0]
        string = aux[1]
        w.insert('1.0', string +'\n'+'\n')
        update(DATA)
    #TOPDOWN:
##    for p in range(len(REFCN_BIAS_P)):
##        step(REFCN_BIAS_P[-1-p])
##        status()
##        time.sleep(0.1615)
##        aux = printdout(SW_BIAS_P[-1-p])
##        DATA[cn+cp+p-1] = aux[0]
##        string = aux[1]
##        w.insert('1.0', string +'\n'+'\n')
##        update(DATA)
##    for n in range(len(REFCN_BIAS_N)):
##        step(REFCN_BIAS_N[n])
##        status()
##        time.sleep(0.1615)
##        aux = printdout(SW_BIAS_N[-1-n])
##        DATA[2*cn+cp+n-2] = aux[0]
##        string = aux[1]
##        w.insert('1.0', string +'\n'+'\n')
##        update(DATA)
    init(LOCKRO,\
        TIACN_TIAG_35_0_RLOAD_010,\
        REFCN_BIAS_N[0],\
        MODECN_OP_MODE_DEEPSLEEP)
    return DATA

############################################################################################
##  TEXT and BUTTONS

def startCV():
    GPIO.output(11,True) ## RED
    GPIO.output(13,False) ## GREEN
    on_change(k)
    w.insert('1.0', ">> Transimpedance value selectec: {}".format(variable_TIA.get())+'\n'+'\n')
    w.insert('1.0', ">> Operation mode selected: {}".format(variable_OPMODE.get())+'\n'+'\n')
    w.insert('1.0', ">> Starting sweep..."+'\n'+'\n')
    print">> Transimpedance value selectec: {}".format(variable_TIA.get()) 
    print ">> Operation mode selected: {}".format(variable_OPMODE.get())
    print ">> Starting cyclic voltammetry..."
    TIA = TIA_dicc["{}".format(variable_TIA.get())]
    OPMODE = OPMODE_dicc["{}".format(variable_OPMODE.get())]
    DATA = sweep(TIA,OPMODE)
    #Lock registers
    write(1,1)
    GPIO.output(11,False) ## RED
    GPIO.output(13,True) ## GREEN
    print "Max current value (uA): {}".format(max(DATA))
    
    #Calibration curves of available substances
    ##############################################
    #Copy this paragraph to add another substance
    #Calibration curve must have logarithmic axis
    if (variable_SUBSTANCE.get()=='Ascorbic Acid'):
            current = max(DATA)
            ########## DATA TO FILL ############
            W = 176.12 #Molecular weight (g/mol)
            m = 0.9033 #Slope of CC
            b = 4.1644 #Offset of CC
            if (v.get()=='')
                V = 1
            else
                V = v.get()
            ####################################
            log_current = math.log10(current)
            log_M = (log_current-b)/m
            M = math.pow(10,log_M)
            mg = (V*W*M)/1000
            print ">> AA (M): %5.3f\n >> AA (mg): %5.3f" %(M,mg)
            #results.insert('1.0', ">> AA (M): %5.3f\n >> AA (mg): %5.3f" %(M,mg))            

    ##############################################

results.insert('1.0', ">> AA (M): 0.001067 \n >> AA (mg): 9.397e-09")

def clearCV():
    a.cla()
    a.set_xlabel('Applied voltage (V)')
    a.set_ylabel('Registered current ('+ u"\u00B5"+'A)')
    a.set_title(k.get())
    data = [0]*20
    a.plot(t,data,'darkblue')
    dataPlot.show()
    init(LOCKWR,\
        TIACN_TIAG_35_0_RLOAD_010,\
        REFCN_BIAS_N[0],\
        MODECN_OP_MODE_DEEPSLEEP)
    ## w.insert('1.0', "Graph removed succesfully!"+'\n'+'\n')
    print('Graph removed succesfully!')
    return 0

def saveCV():
    str = k.get()+".png"
    f.savefig(str, dpi=None, facecolor='w', edgecolor='w',
              orientation='landscape', format='png',
              transparent=False, bbox_inches=None, pad_inches=0.1,
              frameon=False)
    w.insert('1.0', "Graph saved succesfully!"+'\n'+'\n')

def exportCV():
    if (DATA == [0]*20):
        w.insert('1.0', "You can't export data if you have not\n started any sweep :("+'\n'+'\n')
    else:
        str = k.get()+".csv"
        csv_out = open(str, 'wb')
        mywriter = csv.writer(csv_out)
        for row in zip(t, DATA):
            mywriter.writerow(row)
        csv_out.close()
        w.insert('1.0', "Data exported to .csv succesfully!"+'\n'+'\n')
    
def closeCV():
    init(LOCKWR,\
        TIACN_TIAG_35_0_RLOAD_010,\
        REFCN_BIAS_N[0],\
        MODECN_OP_MODE_DEEPSLEEP)
    print('Bye!')
    GPIO.output(13,False) ## GREEN
    root.destroy()
    return 0

TITLE = Label(root, text='Cyclic Voltammetry \nGIT Client Interface')

CONFIG_title = Label(root, text='CONFIGURATION MENU')
INITIALIZE = Label(root, text='INITIALIZE SWEEP')

TIA_label = Label(root,text='Transimpedance gain')
OPMODE_label = Label(root,text='Operation mode')
SUBSTANCE_label = Label(root, text='MEASURING SUBSTANCE')

############################################################################################
##  MAIN MENU

menubar = Menu(root)
menubar.add_command(label="Start", command=startCV)
menubar.add_command(label="Clear",command=clearCV)
menubar.add_command(label="Save graph", command=saveCV)
menubar.add_command(label="Export .csv", command=exportCV)
menubar.add_command(label="Save data to DB")
menubar.add_command(label="Close", command=closeCV)

############################################################################################
##  OPTIONS MENU

variable_TIA = StringVar(root)
variable_TIA.set("Default")
variable_OPMODE = StringVar(root)
variable_OPMODE.set("Default")
variable_SUBSTANCE = StringVar(root)
variable_SUBSTANCE.set("None")

SUBSTANCE = OptionMenu(root, variable_SUBSTANCE, "None", "Ascorbic Acid")

TIA = OptionMenu(root, variable_TIA, "Default", "2.75 KOhms",
                 "3.5 KOhms", "7 KOhms", "14 KOhms",
                 "35 KOhms", "120 KOhms", "350 KOhms")
OPMODE = OptionMenu(root, variable_OPMODE, "Deep Sleep", "2-Lead GRGC",
                 "Standby", "3-Lead AC", "Temperature MT-OFF", "Temperature MT-ON")

def option_changed_SUBSTANCE(*args):
    print "Substance selected: {}".format(variable_SUBSTANCE.get())
    w.insert('1.0', ">> Substance selected: {}".format(variable_SUBSTANCE.get())+'\n'+'\n')

def option_changed_TIA(*args):
    print "Transimpedance value selected: {}".format(variable_TIA.get())
    w.insert('1.0', ">> TIA value selected: {}".format(variable_TIA.get())+'\n'+'\n')
           
def option_changed_OPMODE(*args):
    print "Operation mode selected: {}".format(variable_OPMODE.get())
    w.insert('1.0', ">> Operation mode selected: {}".format(variable_OPMODE.get())+'\n'+'\n')

variable_TIA.trace("w", option_changed_TIA)
variable_OPMODE.trace("w", option_changed_OPMODE)
variable_SUBSTANCE.trace("w", option_changed_SUBSTANCE)

############################################################################################
##  GRID CONFIG

root.grid_columnconfigure(0, minsize=100)
root.grid_columnconfigure(1, minsize=100)
root.grid_columnconfigure(4, minsize=50)
root.grid_rowconfigure(0, minsize=20)
root.grid_rowconfigure(1, minsize=20)
root.grid_rowconfigure(2, minsize=20)
root.grid_rowconfigure(25, minsize=75)

TITLE.grid(column='1',row='1',columnspan='2',rowspan='1')

SUBSTANCE_label.grid(column='1',row='2',columnspan='2',rowspan='1')
SUBSTANCE.grid(column='1',row='3',columnspan='2',rowspan='1')

CONFIG_title.grid(column='1',row='4',columnspan='2',rowspan='1')
TIA_label.grid(column='1',row='5',columnspan='2',rowspan='1')
TIA.grid(column='1',row='6',columnspan='2',rowspan='1')
OPMODE_label.grid(column='1',row='7',columnspan='2',rowspan='1')
OPMODE.grid(column='1',row='8',columnspan='2',rowspan='1')

LOGO = PhotoImage(file='ait.gif')
LOGO = LOGO.subsample(5,5)
Label(root, image=LOGO).grid(column='5',row='1',columnspan='2',rowspan='1')

#GRAPH.grid(column='2',row='2', columnspan='2', rowspan='7')
root.config(menu=menubar)
root.mainloop()                 





############################################################################################




