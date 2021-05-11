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
import cmath
import pylab
from decimal import Decimal
import csv
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT) 
GPIO.setup(13, GPIO.OUT)

root = Tk()
root.wm_title("CVGIT 2019 (C)")
root.geometry('1280x800+100+100')
root.style = Style()
#('clam', 'alt', 'default', 'classic')

root.style.theme_use('clam')

GPIO.output(11,False) ## RED
GPIO.output(13,True) ## GREEN

pb = Progressbar(root, mode='determinate', maximum=300, length=100)
pb.grid(column='1',row='12',columnspan='3',rowspan='1')
pb['length']=350

w = Text(root, width='60', height='12', bg='white', relief = 'groove')
results = Text(root, width='60', height='2', bg='white', relief = 'groove')
#w.grid(column='0',row='12',columnspan='1',rowspan='1')
#results.grid(column='0',row='11',columnspan='1',rowspan='1')
w.grid(column='1',row='9',columnspan='3',rowspan='1')
results.grid(column='1',row='10',columnspan='3',rowspan='1')

w.insert('1.0', 'Welcome to Ciclic Voltammetry Client \n Interface. Please:\n 1) Insert the SPE in the adapters plug.\n 2) Choose your fit config\n    (TIA and OPMODE).\n 3) Click Start and save graph.\n'+'\n'+'\n'+'Technical University of Cartagena'+'\n'+ 'TIC GIT 2017 '+u"\u00A9")
#results.insert('1.0', 'Determined concentration results\n(mg and M)')


GRAPH_title = Label(root, text='Graph title')
GRAPH_title.grid(column='2',row='4',columnspan='2',rowspan='1')
k = Entry(root,width='30')
k.grid(column='2',row='5',columnspan='2',rowspan='1')

interval_title = Label(root, text='Reading Gap Interval')
interval_title.grid(column='1',row='6',columnspan='3',rowspan='1')

int1 = Entry(root,width='15')
int1.grid(column= '1',row='7',columnspan='1',rowspan='1')
int2 = Entry(root,width='15')
int2.grid(column='2',row='7',columnspan='1',rowspan='1')
int3 = Entry(root,width='15')
int3.grid(column='3',row='7',columnspan='1',rowspan='1')


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

TITLE = Label(root, text='Cyclic Voltammetry GIT Client Interface')
INITIALIZE = Label(root, text='INITIALIZE SWEEP')

TIA_label = Label(root,text='TIA gain')
OPMODE_label = Label(root,text='OP mode')
SUBSTANCE_label = Label(root, text='Substance')
METHOD_label = Label(root, text='Amperometric method')



############################################################################################
##  PLOT CONFIG AND SWEEP MAIN FUNCTION

f = Figure(figsize=(5,4), dpi=120, facecolor='white', frameon=False,tight_layout=True)
a = f.add_subplot(111,title='CV 50mV/s - CVGIT',
                  xlabel='v, V',
                  ylabel='i,'+ u"\u00B5"+'A',autoscale_on=True)

##t = SW_BIAS_N + SW_BIAS_P + SW_BIAS_P[::-1] + SW_BIAS_N[::-1]

t_fv = range(1,401)
t_cv = SW_BIAS_P_TOTAL

data_cv = [0]*25
DATA_cv = data_cv
data_fv = [0]*400
DATA_fv = data_fv


###########

def smooth(y,box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y,box,mode='same')
    return y_smooth

############

a.plot(t_cv,data_cv,'blue')
a.grid(True)
#a.plot(t_fv,smooth(data,4),'darkblue')
dataPlot = FigureCanvasTkAgg(f, master=root)
dataPlot.show()
dataPlot.get_tk_widget().grid(column='5',row='3', columnspan='2', rowspan='10')

def on_change(k):
    f = Figure(figsize=(5,4), dpi=120, facecolor='white', frameon=False,tight_layout=True)
    a = f.add_subplot(111,title=k.get(),
    xlabel='v, V',
    ylabel='i,'+ u"\u00B5"+'A',autoscale_on=True)

def update(data, method):
    if method=="Cyclic Voltammetry":
        a.cla()
        a.grid(True)
        a.set_xlabel('v, V')
        a.set_ylabel('i, '+ u"\u00B5"+'A')
        a.set_title(k.get())
        a.plot(t_cv,data,'blue')
        dataPlot.draw()
    if method == "Fixed Voltage":
        a.cla()
        a.grid(True)
        a.set_xlabel('t, s')
        a.set_ylabel('i, '+ u"\u00B5"+'A')
        a.set_title(k.get())
        a.plot(t_fv,smooth(data,4),'blue')
##        a.plot([int(int1.get()),int(int2.get())],[0,0],'r-',lw=5)
##        a.plot([int(int3.get()),299],[0,0],'r-',lw=5)
        a.axvspan(int(int1.get()),int(int2.get()), facecolor='#1f77b4', alpha=0.15)
        a.axvspan(int(int3.get()),299, facecolor='#1f77b4', alpha=0.15)
        dataPlot.draw()

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
    #start_time = time.time()
    #print("--- %s seconds ---" % (time.time() - start_time))

    pb['maximum']=300
    pval = 0
    
    if ("{}".format(variable_METHOD.get())=="Cyclic Voltammetry"):
        for p in range(len(REFCN_BIAS_P_TOTAL)):
            step(REFCN_BIAS_P_TOTAL[p])
            start_time = time.time()
            aux = printdout(SW_BIAS_P_TOTAL[p])
            DATA_cv[p] = aux[0]
            string = aux[1]
            pval = pval + 12
            pb['value']=pval
            pb.update_idletasks()
            w.insert('1.0', string +'\n'+'\n')
            method = "{}".format(variable_METHOD.get())
            update(DATA_cv, method)
            time.sleep(1-(time.time() - start_time))
            print("--- %s seconds ---" % (time.time() - start_time))
        DATA = DATA_cv
            
    elif ("{}".format(variable_METHOD.get())=="Fixed Voltage"):
        for p in range(400):
            #step('10100101') # -0.2
            #step('10110110') #+0.25
            #step('10110111') # +0.3
            step('10111000') # +0.35
            #step('10111001') # +0.4
            #step('10111010') # + 0.45
            #step('10111011') # + 0.5
            start_time = time.time() 
            aux = printdout(p)
            DATA_fv[p] = aux[0]
            string = aux[1]
            #pval = pval + 1
            #pb['value']=pval
            #pb.update_idletasks()
            w.insert('1.0', string +'\n'+'\n')
            method = "{}".format(variable_METHOD.get())
            update(DATA_fv, method)
            time.sleep(1-(time.time() - start_time))
            print("--- %s seconds ---" % (time.time() - start_time))
        DATA = DATA_fv
    else:
        w.insert('1.0', 'Choose a right method' +'\n'+'\n')

    pb.stop()
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
    SUBSTANCE = "{}".format(variable_SUBSTANCE.get())
    DATA = sweep(TIA,OPMODE)
    #method = "{}".format(variable_METHOD.get())
    #update(DATA, method)
    
    str = "Results/"+k.get()+".csv"
    if ("{}".format(variable_METHOD.get())=="Cyclic Voltammetry"):
        csv_out = open(str, 'wb')
        mywriter = csv.writer(csv_out)
        for row in zip(t_cv, DATA):
            mywriter.writerow(row)
        csv_out.close()
        w.insert('1.0', "Data exported to .csv succesfully!"+'\n'+'\n')
        
    elif ("{}".format(variable_METHOD.get())=="Fixed Voltage"):
        # AUTOMATIC LEVEL
        mean2 = np.mean(DATA[int(int3.get()):399])
        mean1 = np.mean(DATA[int(int1.get()):int(int2.get())])
        gap = (mean1-mean2)*1000

        print ">> Gap (nA): %5.5f" %(gap)
        w.insert('1.0', ">> Mean1 (nA): %5.5f" %(mean1) +'\n'+'\n')
        w.insert('1.0', ">> Mean2 (nA): %5.5f" %(mean2) +'\n'+'\n')

        # .CSV CREATION
        csv_out = open(str, 'wb')
        mywriter = csv.writer(csv_out)
        for row in zip(t_fv, DATA):
            mywriter.writerow(row)
        csv_out.close()
        
        w.insert('1.0', "Data exported to .csv succesfully!"+'\n'+'\n')
        
    #Lock registers
    write(1,1)
    GPIO.output(11,False) ## RED
    GPIO.output(13,True) ## GREEN
    print "Max current value (uA): {}".format(max(DATA))
    
    #Calibration curves of available substances
    ##############################################
    #Copy this paragraph to add another substance
    #Calibration curve must have logarithmic axis
    if (SUBSTANCE=='Ascorbic Acid'):
            current = max(DATA)
            ########## DATA TO FILL ############
            W = 176.12 #Molecular weight (g/mol)
            m = 0.9033 #Slope of CC
            b = 4.1644 #Offset of CC
            V = 1
            ####################################
            log_current = math.log10(current)
            log_M = (log_current-b)/m
            M = math.pow(10,log_M)
            mg = (V*W*M)/1000
            print ">> AA (M): %5.5f\n >> AA (mg): %5.5f" %(M,mg)
            results.insert('1.0', ">> AA (M): %5.5f  \n >> AA (mg): %5.5f " %(M,mg))

    ##############################################
    if (variable_SUBSTANCE.get()=='Progesterone'):
            current = max(DATA)
            ########## DATA TO FILL ############
            W = 176.12 #Molecular weight (g/mol)
            m = 0.9033 #Slope of CC
            b = 4.1644 #Offset of CC
            V = 1
            ####################################
            log_current = math.log10(current)
            log_M = (log_current-b)/m
            M = math.pow(10,log_M)
            mg = (V*W*M)/1000
            print ">> AA (M): %5.5f\n >> AA (mg): %5.5f" %(M,mg)
            results.insert('1.0', ">> AA (M): %5.5f  \n >> AA (mg): %5.5f " %(M,mg))

    ##############################################

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
    str =  "Results/"+k.get()+".png"
    f.savefig(str, dpi=None, facecolor='w', edgecolor='w',
              orientation='landscape', format='png',
              transparent=False, bbox_inches=None, pad_inches=0.1,
              frameon=False)
    w.insert('1.0', "Graph saved succesfully!"+'\n'+'\n')

def exportCV():
    if ("{}".format(variable_METHOD.get())=="Cyclic Voltammetry"):
        str = k.get()+".csv"
        csv_out = open(str, 'wb')
        mywriter = csv.writer(csv_out)
        for row in zip(t_cv, DATA):
            mywriter.writerow(row)
        csv_out.close()
        w.insert('1.0', "Data exported to .csv succesfully!"+'\n'+'\n')
    elif ("{}".format(variable_METHOD.get())=="Fixed Voltage"):
        str = k.get()+".csv"
        csv_out = open(str, 'wb')
        mywriter = csv.writer(csv_out)
        for row in zip(t_fv, DATA):
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

############################################################################################
##  MAIN MENU

menubar = Menu(root)
menubar.add_command(label="Start", command=startCV)
menubar.add_command(label="Clear",command=clearCV)
menubar.add_command(label="Save graph", command=saveCV)
#menubar.add_command(label="Export .csv", command=exportCV)
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
variable_METHOD = StringVar(root)
variable_METHOD.set("None")

SUBSTANCE = OptionMenu(root, variable_SUBSTANCE, "None", "Ascorbic Acid", "Progesterone")
METHOD = OptionMenu(root, variable_METHOD, "None", "Cyclic Voltammetry", "Fixed Voltage")

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

def option_changed_METHOD(*args):
    print "Method selected: {}".format(variable_METHOD.get())
    w.insert('1.0', ">> Method selected: {}".format(variable_METHOD.get())+'\n'+'\n')

variable_TIA.trace("w", option_changed_TIA)
variable_OPMODE.trace("w", option_changed_OPMODE)
variable_SUBSTANCE.trace("w", option_changed_SUBSTANCE)
variable_METHOD.trace("w", option_changed_METHOD)


############################################################################################
##  GRID CONFIG

root.grid_columnconfigure(0, minsize=60)

root.grid_columnconfigure(1, minsize=100)
root.grid_columnconfigure(2, minsize=100)
root.grid_columnconfigure(3, minsize=100)
root.grid_columnconfigure(4, minsize=60)

##root.grid_rowconfigure(2, minsize=100)

TITLE.grid(column='1',row='1',columnspan='3',rowspan='1')

SUBSTANCE_label.grid(column='1',row='2',columnspan='1',rowspan='1')
SUBSTANCE.grid(column='1',row='3',columnspan='1',rowspan='1')

METHOD_label.grid(column='2',row='2',columnspan='1',rowspan='1')
METHOD.grid(column='2',row='3',columnspan='1',rowspan='1')

TIA_label.grid(column='3',row='2',columnspan='1',rowspan='1')
TIA.grid(column='3',row='3',columnspan='1',rowspan='1')

OPMODE_label.grid(column='1',row='4',columnspan='1',rowspan='1')
OPMODE.grid(column='1',row='5',columnspan='1',rowspan='1')

LOGO = PhotoImage(file='ait.gif')
LOGO = LOGO.subsample(5,5)
Label(root, image=LOGO).grid(column='5',row='1',columnspan='3',rowspan='1')

#GRAPH.grid(column='2',row='2', columnspan='2', rowspan='7')
root.config(menu=menubar)
root.mainloop()                 


