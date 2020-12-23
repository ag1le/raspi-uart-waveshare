#!/usr/bin/env python3
# Copyright (c) 2020 Mauri Niininen
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time
import numpy as np

from random import randint
import RPi.GPIO as GPIO

from waveshare.epaper import EPaper
from waveshare.epaper import Handshake
from waveshare.epaper import RefreshAndUpdate
from waveshare.epaper import SetPallet
from waveshare.epaper import DrawCircle
from waveshare.epaper import FillCircle
from waveshare.epaper import DrawRectangle
from waveshare.epaper import FillRectangle
from waveshare.epaper import DrawTriangle
from waveshare.epaper import DrawLine
from waveshare.epaper import FillTriangle
from waveshare.epaper import DisplayText
from waveshare.epaper import SetCurrentDisplayRotation
from waveshare.epaper import SetEnFontSize
from waveshare.epaper import SetZhFontSize
from waveshare.epaper import ClearScreen


class Plot():

    def __init__(self, paper):
        self.paper = paper
        self.shim =16  #shim value to let a margin of edge pixels - not to exceed 800x600 size display 
        box = self.rect(0+self.shim,0+self.shim,800-self.shim,600-self.shim)
        self.paper.send(DrawRectangle(box.x0,box.y0,box.x1,box.y1))

    def rect(self, x0, y0, x1, y1):
        """rectangle to plot the values in"""
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        return self

    def figure(figsize=(800, 600)):
        self.x1 = figsize[0]
        self.y1 = figsize[1]

    def translate(value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return int(rightMin + (valueScaled * rightSpan))

    def xticks(self, ticks=np.arange(0, 1, step=0.2),labels=["1","2","3","4","5"]):
        for tick,label in zip(ticks,labels):
            x = Plot.translate(tick, 0, 1, self.x0+self.shim, self.x1-self.shim)
            print(f"xticks:{x} y:{self.y1}")
            self.paper.send(DrawLine(x,self.y1,x,self.y1+self.shim))
            self.paper.send(DisplayText(x,self.y1-self.shim,f"{label}".encode("gb2312")))

    def yticks(self, ticks=np.arange(0, 1, step=0.1),labels=None):
        for tick,label in zip(ticks,labels):
            y = self.y1 -Plot.translate(tick, 0, 1, self.y0+self.shim, self.y1-self.shim)
            print(f"yticks:{y} x:{self.x0}")
            self.paper.send(DrawLine(self.x0,y,self.x0-self.shim,y))
            self.paper.send(DisplayText(self.x0-self.shim,y,f"{label}".encode("gb2312")))

    def plot(self, values, marker='t', data_label=False):
        self.min_y_value, self.max_y_value = min(values), max(values)
        self.min_x_value, self.max_x_value = 0, len(values)
        #print(f"min_x_value:{min_x_value} max_x_value:{max_x_value}")
        y0 = Plot.translate(values[0], self.min_y_value, self.max_y_value, self.y0, self.y1)
        x0 = self.x0
        for i, value in enumerate(values):
            x1 = self.x0 + Plot.translate(i, self.min_x_value, self.max_x_value, self.x0+self.shim, self.x1-self.shim)
            y1 = self.y1 - Plot.translate(value, self.min_y_value, self.max_y_value, self.y0+self.shim, self.y1-self.shim)
            print(f"x0:{x0} x1:{x1} y0:{y0} y1:{y1} value:{value}")
            self.paper.send(DrawLine(x0,y0,x1,y1))
            if marker == 'o':
                self.paper.send(DrawCircle(x1,y1,self.shim))
                self.paper.send(FillCircle(x1,y1,self.shim))
            elif marker == 't':
                self.paper.send(DrawTriangle(x1-int(self.shim/2),y1-int(self.shim/2),x1,y1+int(self.shim/2), x1+int(self.shim/2),y1-int(self.shim/2)))
                self.paper.send(FillTriangle(x1-int(self.shim/2),y1-int(self.shim/2),x1,y1+int(self.shim/2), x1+int(self.shim/2),y1-int(self.shim/2)))
            elif marker == 's':
                self.paper.send(DrawRectangle(x1-self.shim,y1-self.shim,x1+self.shim,y1+self.shim))
                self.paper.send(FillRectangle(x1-self.shim,y1-self.shim,x1+self.shim,y1+self.shim))                
            if data_label: 
                self.paper.send(DisplayText(x1,y1,f"{value}".encode("gb2312")))
            x0, y0 = x1, y1

values = [23,18,0,26,26,32,31,28,27,26,24,23,23]
#values = [randint(0,45) for i in range(0,50)]




def main():
    with EPaper() as paper:

        plt = Plot(paper)
        plt.plot(values)
        plt.xticks()
        step = (max(values)-min(values))/10.
        lbls = [f"{int(val)}" for val in np.arange(min(values),max(values),step)]
        print("labels:", lbls)
        plt.yticks(labels=lbls)




if __name__ == '__main__':

    main()
