#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import calendar
import pathlib
import statistics
import pandas as pd
import numpy as np
import seaborn
import matplotlib.pyplot as plt
from activity import Activity, create_activity, parse_activities_csv, build_activity_dataframe, extract_activities

def heatmap(arguments):
    rides = extract_activities(arguments.input, imperial=True, type_filter="Ride")

    current_datetime = datetime.datetime.now()
    rides = [ride for ride in rides if ride.date.year == current_datetime.year]

    weekday_df = pd.DataFrame(data={
        "weekday": [ride.date.weekday() for ride in rides],
        "week_of_year": [ride.date.strftime("%U") for ride in rides],
        "distance": [ride.distance for ride in rides]
    })
    weekday_pivot = weekday_df.pivot(index="weekday", columns="week_of_year", values="distance")

    plt.clf()
    seaborn.set_theme()
    palette = seaborn.color_palette("crest", as_cmap=True)
    grid_kws = {"height_ratios": (.9, .05), "hspace": .05}
    figure, (ax, cbar_ax) = plt.subplots(2, gridspec_kw=grid_kws)
    ax = seaborn.heatmap(weekday_pivot,
        ax=ax,
        cbar_ax=cbar_ax,
        linewidths=1.0,
        cbar_kws={"orientation": "horizontal"},
        square=True,
        cmap=palette,
        xticklabels=1,
        yticklabels=1)
    ax.set(xlabel=None, ylabel=None)

    vertical_labels = ax.get_yticklabels()
    for label in vertical_labels:
        label.set_text(calendar.day_abbr[int(label.get_text())])
    ax.set_yticklabels(vertical_labels, rotation=0, horizontalalignment="right", fontsize="x-small")

    horizontal_labels = ax.get_xticklabels()
    last_label = None
    for label in horizontal_labels:
        week_of_year = int(label.get_text())
        rough_datetime = datetime.datetime.strptime("{}-{}-1".format(current_datetime.year, week_of_year), "%Y-%W-%w")
        rough_month = calendar.month_abbr[rough_datetime.month]
        if last_label is None or last_label != rough_month:
            label.set_text(rough_month)
        else:
            label.set_text(None)
        last_label = rough_month
    ax.set_xticklabels(horizontal_labels, rotation=45, fontsize="x-small")
    plt.title("Daily Distances, Year to Date")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "heatmap.svg"))

    if arguments.show:
        plt.show()


def average_distance_over_weekday(arguments):
    rides = extract_activities(arguments.input, imperial=True, type_filter="Ride")

    weekdays_by_index = dict(zip(range(7), calendar.day_name))
    distances_by_index = dict(zip(range(7), [[] for x in range(7)]))
    for activity in rides:
        distances_by_index[activity.date.weekday()].append(activity.distance)

    average_distances = [statistics.mean(weekday_distances) for index, weekday_distances in distances_by_index.items()]

    adow_df = pd.DataFrame(data={
        "weekday": [weekdays_by_index[index] for index, distance in enumerate(average_distances)],
        "distances": average_distances
    })
    
    plt.clf()
    seaborn.set_theme()
    adow_plot = seaborn.barplot(x="weekday", y="distances", data=adow_df)
    adow_plot.set(xlabel="Day of Week", ylabel="Average Distance (miles)")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "adow.svg"))
    
    if arguments.show:
        plt.show()


def elevation_time_speed(arguments):
    rides = extract_activities(arguments.input, imperial=True, type_filter="Ride")

    ets_df = pd.DataFrame(data={
        "elevation": [float(activity.elevation_gain) for activity in rides],
        "moving_time": [float(activity.moving_time) / 60 for activity in rides],
        "average_speed": [float(activity.average_speed) * 2.237 if activity.average_speed else 0 for activity in rides]
    })

    plt.clf()
    seaborn.set_theme()
    ets_pivot = pd.pivot_table(ets_df, index="elevation", columns="moving_time", values="average_speed", aggfunc=np.average)
    f, ax = plt.subplots(figsize=(9, 6))
    ets_plot = seaborn.heatmap(ets_pivot, annot=True, linewidths=0.5, ax=ax)

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "ets.svg"))
    
    if arguments.show:
        plt.show()


def average_speed_over_activities(arguments):
    rides = extract_activities(arguments.input, imperial=True, type_filter="Ride")

    asot_df = pd.DataFrame(data={
        "activity_date": [activity.date for activity in rides],
        "average_speed": [activity.average_speed if activity.average_speed else 0 for activity in rides]
    })

    plt.clf()
    seaborn.set_theme()
    asot_plot = seaborn.lineplot(x="activity_date", y="average_speed", data=asot_df)
    asot_plot.set(xlabel="Date", ylabel="Average Speed (mph)")
    plt.fill_between(asot_df.activity_date.values, asot_df.average_speed.values)

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "asot.svg"))
    
    if arguments.show:
        plt.show()


def distance_over_time(arguments):
    """Do a basic scatterplot of distance over ride time."""
    rides = extract_activities(arguments.input, imperial=True, type_filter="Ride")

    dot_by_id = {
        "distance": [ride.distance for ride in rides],
        "moving_time": [ride.moving_time / 60 for ride in rides],
        "average_speed": [ride.average_speed for ride in rides]
    }

    plt.clf()
    seaborn.set_theme()
    dot_df = pd.DataFrame(data=dot_by_id)
    dot_plot = seaborn.lmplot(x="moving_time", y="distance", data=dot_df)
    dot_plot.set(xlabel="Moving Time (Minutes)", ylabel="Distance (Miles)")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "dot.svg"))

    if arguments.show:
        plt.show()


def distance_histogram(arguments):
    rides = extract_activities(arguments.input, imperial=True, type_filter="Ride")

    distance_df = pd.DataFrame(data={
        "distance": [ride.distance for ride in rides]
    })
    
    plt.clf()
    seaborn.set_theme()
    distance_plot = seaborn.displot(distance_df, x="distance", binwidth=2)
    distance_plot.set(xlabel="Distance (miles)", ylabel="Count")
    # plt.title("Distribution of Ride Distances")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "dhist.svg"))
    
    if arguments.show:
        plt.show()


def moving_time_histogram(arguments):
    rides = extract_activities(arguments.input, imperial=True, type_filter="Ride")

    time_df = pd.DataFrame(data={
        "moving_time": [ride.moving_time / 60 for ride in rides]
    })

    plt.clf()
    seaborn.set_theme()
    time_plot = seaborn.displot(time_df, x="moving_time", binwidth=15)
    time_plot.set(xlabel="Moving Time (minutes)", ylabel="Count")
    # plt.title("Distribution of Ride Times")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "thist.svg"))
    
    if arguments.show:
        plt.show()
