#!/usr/bin/env python3
""" plotting to waveshare 4.3 e-paper using matplotlib.pyplot like interface"""
# Copyright (c) 2020 Mauri Niininen
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from random import randint
import numpy as np


from waveshare.epaper import EPaper
from waveshare.epaper import DrawCircle
from waveshare.epaper import FillCircle
from waveshare.epaper import DrawRectangle
from waveshare.epaper import FillRectangle
from waveshare.epaper import DrawTriangle
from waveshare.epaper import DrawLine
from waveshare.epaper import FillTriangle
from waveshare.epaper import DisplayText


class Plot:
    """ Emulate matplotlib.pyplot interface for plotting """
    def __init__(self, paper):
        self.paper = paper
        # shim value to let a margin of edge pixels - not to exceed 800x600 size display
        self.shim = 16
        box = self.rect(0 + self.shim, 0 + self.shim, 800 - self.shim, 600 - self.shim)
        self.paper.send(DrawRectangle(box.x_0, box.y_0, box.x_1, box.y_1))

    def rect(self, x_0, y_0, x_1, y_1):
        """rectangle to plot the values in"""
        self.x_0 = x_0
        self.x_1 = x_1
        self.y_0 = y_0
        self.y_1 = y_1
        return self

    @staticmethod
    def translate(value, left_min, left_max, right_min, right_max):
        """ Translate coordinate values """
        # Figure out how 'wide' each range is
        left_span = left_max - left_min
        right_span = right_max - right_min

        # Convert the left range into a 0-1 range (float)
        value_scaled = float(value - left_min) / float(left_span)

        # Convert the 0-1 range into a value in the right range.
        return int(right_min + (value_scaled * right_span))

    def xticks(self, ticks=np.arange(0, 1, step=0.2), labels=[]):
        """"Draw x-axis tick lines and labels"""
        for tick, label in zip(ticks, labels):
            x_tick = Plot.translate(tick, 0, 1, self.x_0 + self.shim, self.x_1 - self.shim)
            self.paper.send(DrawLine(x_tick, self.y_1, x_tick, self.y_1 + self.shim))
            self.paper.send(
                DisplayText(x_tick, self.y_1 - self.shim, f"{label}".encode("gb2312"))
            )

    def yticks(self, ticks=np.arange(0, 1, step=0.1), labels=[]):
        """"Draw y-axis tick lines and labels"""
        for tick, label in zip(ticks, labels):
            y_tick = self.y_1 - Plot.translate(
                tick, 0, 1, self.y_0 + self.shim, self.y_1 - self.shim
            )
            self.paper.send(DrawLine(self.x_0, y_tick, self.x_0 - self.shim, y_tick))
            self.paper.send(
                DisplayText(self.x_0 - self.shim, y_tick, f"{label}".encode("gb2312"))
            )

    def plot(self, data, marker="t", data_label=False):
        """" Plot data """
        min_y_value, max_y_value = min(data), max(data)
        min_x_value, max_x_value = 0, len(data)
        # print(f"min_x_value:{min_x_value} max_x_value:{max_x_value}")
        y_0 = Plot.translate(data[0], min_y_value, max_y_value, self.y_0, self.y_1)
        x_0 = self.x_0
        for i, value in enumerate(data):
            x_1 = self.x_0 + Plot.translate(
                i,
                min_x_value,
                max_x_value,
                self.x_0 + self.shim,
                self.x_1 - self.shim,
            )
            y_1 = self.y_1 - Plot.translate(
                value,
                min_y_value,
                max_y_value,
                self.y_0 + self.shim,
                self.y_1 - self.shim,
            )
            #print(f"x_0:{x_0} x_1:{x_1} y_0:{y_0} y_1:{y_1} value:{value}")
            self.paper.send(DrawLine(x_0, y_0, x_1, y_1))
            if marker == "o":
                self.paper.send(DrawCircle(x_1, y_1, self.shim))
                self.paper.send(FillCircle(x_1, y_1, self.shim))
            elif marker == "t":
                self.paper.send(
                    DrawTriangle(
                        x_1 - int(self.shim / 2),
                        y_1 - int(self.shim / 2),
                        x_1,
                        y_1 + int(self.shim / 2),
                        x_1 + int(self.shim / 2),
                        y_1 - int(self.shim / 2),
                    )
                )
                self.paper.send(
                    FillTriangle(
                        x_1 - int(self.shim / 2),
                        y_1 - int(self.shim / 2),
                        x_1,
                        y_1 + int(self.shim / 2),
                        x_1 + int(self.shim / 2),
                        y_1 - int(self.shim / 2),
                    )
                )
            elif marker == "s":
                self.paper.send(
                    DrawRectangle(
                        x_1 - self.shim, y_1 - self.shim, x_1 + self.shim, y_1 + self.shim
                    )
                )
                self.paper.send(
                    FillRectangle(
                        x_1 - self.shim, y_1 - self.shim, x_1 + self.shim, y_1 + self.shim
                    )
                )
            if data_label:
                self.paper.send(DisplayText(x_1, y_1, f"{value}".encode("gb2312")))
            x_0, y_0 = x_1, y_1


values = [23, 18, 0, 26, 26, 32, 31, 28, 27, 26, 24, 23, 23]
values = [randint(0, 45) for i in range(0, 50)]


def main():
    """ main function"""
    with EPaper() as paper:

        plt = Plot(paper)
        plt.plot(values)
        plt.xticks()
        step = (max(values) - min(values)) / 10.0
        lbls = [f"{int(val)}" for val in np.arange(min(values), max(values), step)]
        #print("labels:", lbls)
        plt.yticks(labels=lbls)


if __name__ == "__main__":

    main()
