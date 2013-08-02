DX=000

import sys, serial,glob,os
import numpy as np
from time import sleep
from collections import deque
from matplotlib import pyplot as plt
color=['red','blue','yellow','magenta','cyan','burlywood','black', 'chartreuse', 'navy']

#timeout = None
def read_until(con, until):
    buf=""
    ler = con.read(1)
    buf+=ler
    while ler!=until:
        ler = con.read(1)
        if ler == '' :
            sleep(0.02)
            continue
        buf = buf + ler
    return buf


# class that holds analog data for N samples
class AnalogData:
  # constr
  def __init__(self, maxLen,j):
    self.ax = [[]]
    self.ay = [[]]
    for k in range(j):
        self.ax.append([])
        self.ay.append([])
    self.maxLen = maxLen
 
  # ring buffer
  def addToBuf(self, buf, val):
    if len(buf) < self.maxLen:
      buf.append(val)
    else:
      buf.pop()
      buf.appendleft(val)
  # add data
  def add(self, data):
    assert(len(data) == 3)
    self.ax[int(data[0])].append(data[1])
    self.ay[int(data[0])].append(data[2])

########################################
# PLOT CLASS
########################################
class AnalogPlot:
  # constr
  def __init__(self, analogData):
    # set plot to animated
    plt.ion() 
    self.axline=[]
  def init(self,analogData,j):
    for i in range(j):
        self.axline.append(plt.plot(analogData.ax[i],analogData.ay[i],color=color[i]))
    plt.ylim([0, 10])
    plt.xlim([0, 1000])
 
  # update plot
  def update(self, analogData, j):
#    print self.axline
    self.axline[j][0].set_xdata(analogData.ax[j])
    self.axline[j][0].set_ydata(analogData.ay[j])
    xmin, xmax = plt.xlim()
    xmax2=max(analogData.ax[j])
    if xmax2 > xmax:
        xmax=1.3*xmax2
        if DX > 0:
            plt.xlim([xmax2-DX,xmax2])
        else:
            plt.xlim([0,xmax])
    ymin, ymax = plt.ylim()
    ymax2=max(analogData.ay[j])
    ymin2=min(analogData.ay[j])
    if ymax2 > ymax:
        ymax=1.3*ymax2
        if ymin<ymin2:
            plt.ylim([0,ymax])
        else:
            plt.ylim([1.2*ymin2,ymax])
#    self.axline[1][0].set_xdata(analogData.ax[1])
#    self.axline[1][0].set_ydata(analogData.ay[1])

    plt.draw()
 
# main() function
def main():
    # plot parameters
 
    x_label="X"
    y_label="Y"
    data_label=[""]
    ##############################
    # START GRAPH COMUNICATION
    ##############################
    os.system('clear')
    print "Starting graph configuration"
    num_line=6
#    num_line=input("How many lines you will plot (1-6)?   ")
#    num_line=int(num_line)
#    while num_line>6 or num_line<1:
#        print "Please, don't mess with me!"
#        num_line=input("How many lines you will plot? (1-6)")
#        num_line=int(num_line)
#    for k in range(num_line):
#            data_label.append("");
#    final="end"
#    while final!="end":
#        i=raw_input("command: ")
#        i=i.split("=")
#        final=i[0]
#        if(final=="xlabel"):
#            x_label=i[1]
#        elif(final=="ylabel"):
#            y_label=i[1]
#        elif(final=="label"):
#            data_label[int(i[1])-1]=i[2]
#        elif (final== "end"):
#            print "Rock'n Roll Baby!"
#        else:
#            lixo = raw_input("Need any help?")
#            sleep(1)
#            print "Read the Fucking Manual! =)"
    
    
    analogData = AnalogData(500,num_line)
    
    
    ##############################
    # START ARDUINO COMUNICATION
    ##############################
    os.system('clear')
    print "======= List of USB devices ======="
    serial_ports = glob.glob('/dev/ttyUSB*')
    while(len(serial_ports)==0):
        print "Connect the Arduino..."
        sleep(5);
        serial_ports = glob.glob('/dev/ttyUSB*')
    for i in range(len(serial_ports)):
        print i, " - ", serial_ports[i]
    port=raw_input("Choose the arduino port (e.g. 0): ")
    #    port=0
    ser = serial.Serial(serial_ports[int(port)], 9600)
    sleep(1);
    line=''
    while(len(line)!=3):
        line=read_until(ser,"\n").split(";")
    print "Arduino connected moving on..."
    
    analogPlot = AnalogPlot(analogData)
    analogPlot.init(analogData,num_line)
    while True:
        try:
            line=read_until(ser,"\n").rstrip()
            data = [float(val) for val in line.split(";")]
            data[0]=data[0]-1.
            if(len(data) == 3):
                analogData.add(data)
                analogPlot.update(analogData,int(data[0]))
        except KeyboardInterrupt:
            print 'exiting'
            break
    ser.flush()
    ser.close()
 
# call main
if __name__ == '__main__':
  main()