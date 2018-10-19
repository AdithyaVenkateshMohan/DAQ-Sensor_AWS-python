#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 13:17:23 2017

@author: dieter
"""
import Sonar
import tkinter as tk
import configparser
from tkinter import W, E, N, S
import library
import os
import time
import numpy
import sweep
import pandas

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure


# def take_snapshot(self, event):
#    # if self.run_on_robot: print 'Take SnapShot'
#    image_data = self.client.take_snapshot()
#    self.last_image = Image.open(StringIO.StringIO(image_data))
#    self.last_image = ImageTk.PhotoImage(self.last_image)
#    self.image_label.configure(image=self.last_image)
#    self.master.update()

class HelloApp:
    def __init__(self, master):
        self.use_board = True

        self.folder_name = tk.StringVar()
        self.counter_value = tk.IntVar()
        self.repeat_value = tk.IntVar()
        self.status_value = tk.StringVar()

        # Figure
        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.axis1 = self.fig.add_subplot(121)
        self.axis2 = self.fig.add_subplot(122)

        # Define widgets
        self.master = master
        self.folder = tk.Entry(textvariable=self.folder_name, width=30)
        self.repeats = tk.Entry(textvariable=self.repeat_value, width=10, justify=tk.CENTER)
        self.counter = tk.Label(textvariable=self.counter_value, width=10, justify=tk.CENTER)
        self.status = tk.Message(textvariable=self.status_value, width=500)
        self.measure = tk.Button(master, text="Measure")

        # Figure widget
        self.canvas = FigureCanvasTkAgg(self.fig, self.master)
        self.canvas_widget = self.canvas.get_tk_widget()

        # Add the widgets to their parents
        self.folder.grid(row=0, column=0, columnspan=2, sticky=W + E)
        self.counter.grid(row=0, column=2, sticky=W + E)
        self.repeats.grid(row=1, column=0, sticky=W + E)
        self.measure.grid(row=2, column=0, sticky=W + E)
        self.status.grid(row=4, column=0, columnspan=3, sticky=W + E)
        self.canvas_widget.grid(row=3, column=0, columnspan=3)

        # Read settings
        self.settings = configparser.ConfigParser()
        self.settings.read('settings.txt')

        # Prepare Sonar
        self.sonar = Sonar.Sonar()
        self.sonar.connect()
        start_freq = self.settings.getint('sonar', 'start_freq')
        end_freq = self.settings.getint('sonar', 'end_freq')
        samples = self.settings.getint('sonar', 'samples')
        self.sonar.set_signal(start_freq, end_freq, samples)
        self.sonar.build_charge()

        # Bindings
        self.measure.bind('<ButtonPress>', self.do_measurement)
        # master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Set initial values
        self.counter_value.set(0)
        self.repeat_value.set(3)
        self.status_value.set('Ready')

    def do_measurement(self, event):
        folder = self.folder_name.get()
        if folder == '': return
        data_folder = os.path.join('data', folder)
        library.make_folder(data_folder)
        files = library.get_files(data_folder)
        numbers = library.extract_numbers(files)
        current_counter = max(numbers) + 1
        current_counter_str = str(current_counter).rjust(4, '0')
        self.counter_value.set(current_counter)
        repeats = self.repeat_value.get()
        pause = self.settings.getfloat('sonar', 'pause')

        all_data = numpy.empty((7000, 2, repeats))
        for repetition in range(repeats):
            message = 'Performing measurement %s, %i/%i ' % (current_counter_str, repetition + 1, repeats)
            self.status_value.set(message)
            self.status.update_idletasks()
            data = self.sonar.measure()
            data = Sonar.convert_data(data, 7000)
            all_data[:, :, repetition] = data
            time.sleep(pause)

        self.axis1.clear()
        self.axis1.plot(data)
        self.canvas.draw()

        output_file = os.path.join(data_folder, 'measurement' + current_counter_str + '.npy')
        numpy.save(output_file, all_data)

        message = 'Performing lidar measurement'
        self.status_value.set(message)
        self.status.update_idletasks()

        lidar_data = sweep.scan(3)
        plot_data = lidar_data[lidar_data['strength'] > 50]
        plot_data['round'] = numpy.round(plot_data['degrees'])

        mns = plot_data.groupby('degrees')
        mns = mns.mean()
        mns = mns.reset_index()

        self.axis2.clear()
        self.axis2.scatter(mns['x'], mns['y'], s=0.1)
        self.axis2.axis('equal')
        self.canvas.draw()

        output_file = os.path.join(data_folder, 'measurement' + current_counter_str + '.csv')
        lidar_data.to_csv(output_file)

        message = 'Measurement %s completed' % (current_counter_str)
        self.status_value.set(message)
        self.status.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = HelloApp(root)
    root.mainloop()
