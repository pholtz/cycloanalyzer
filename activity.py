#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import datetime
import pandas as pd
import pathlib
import zipfile

def extract_activities(user_filepath, imperial=True, type_filter=None):
    """Source, extract, and parse a given activity archive."""
    extracted_filepath = source_input_directory(user_filepath)
    activities = parse_activities_csv(extracted_filepath, imperial, type_filter)
    return activities

def source_input_directory(user_filepath):
    """Examine program arguments to determine the location of an archive.
    Extract as needed.
    """
    if user_filepath is None:
        return "export"

    path = pathlib.Path(user_filepath)
    if not path.exists():
        raise RuntimeError("Specified path {} does not exist".format(user_filepath))

    if path.is_dir():
        return user_filepath

    if path.is_file():
        if user_filepath.endswith(".zip"):
            extracted_filepath = user_filepath.replace(".zip", "")
            with zipfile.ZipFile(user_filepath, 'r') as zip_file:
                zip_file.extractall(extracted_filepath)
                return extracted_filepath
        else:
            raise RuntimeError("Specified path {} is a file, but not an archive".format(user_filepath))


def parse_activities_csv(extract_filepath, imperial=True, type_filter=None):
    """Ingest extracted activities csv and return a list of parsed acitivty instances."""
    activities = []
    activities_filepath = os.path.join(extract_filepath, "activities.csv")
    with open(activities_filepath, "r") as activities_file:
        activities_reader = csv.DictReader(activities_file)
        for activity_record in activities_reader:
            activity = create_activity(activity_record) 
            if imperial:
                activity.convert_to_imperial()
            if type_filter and activity.activity_type != type_filter:
                continue
            activities.append(activity)
    return activities


def build_activity_dataframe(imperial=True, type_filter=None):
    activities = parse_activities_csv(imperial, type_filter)
    activities_by_field = {
        "date": [],
        "name": [],
        "activity_type": [],
        "distance": [],
        "moving_time": [],
        "average_speed": [],
        "elevation_gain": []
    }
    for activity in activities:
        activities_by_field["date"].append(activity.date)
        activities_by_field["name"].append(activity.name)
        activities_by_field["activity_type"].append(activity.activity_type)
        activities_by_field["distance"].append(activity.distance)
        activities_by_field["moving_time"].append(activity.moving_time)
        activities_by_field["average_speed"].append(activity.average_speed)
        activities_by_field["elevation_gain"].append(activity.elevation_gain)
    return pd.DataFrame(data=activities_by_field)


def create_activity(activity_record):
    """Given a csv dictionary record, create an activity instance with typing and defaults set appropriately."""
    activity = Activity()
    activity.activity_id = activity_record["Activity ID"]
    activity.date = datetime.datetime.strptime(activity_record["Activity Date"], "%b %d, %Y, %I:%M:%S %p")
    activity.name = activity_record["Activity Name"]
    activity.activity_type = activity_record["Activity Type"]
    activity.elapsed_time = float(activity_record["Elapsed Time"] or 0)
    activity.distance = float(activity_record["Distance"] or 0)
    activity.filename = activity_record["Filename"]
    activity.moving_time = float(activity_record["Moving Time"] or 0)
    activity.max_speed = float(activity_record["Max Speed"] or 0)
    activity.average_speed = float(activity_record["Average Speed"] or 0)
    activity.elevation_gain = float(activity_record["Elevation Gain"] or 0)
    activity.elevation_low = float(activity_record["Elevation Low"] or 0)
    activity.elevation_high = float(activity_record["Elevation High"] or 0)
    activity.max_grade = float(activity_record["Max Grade"] or 0)
    activity.average_grade = float(activity_record["Average Grade"] or 0)
    activity.perceived_exertion = float(activity_record["Perceived Exertion"] or 0)
    activity.perceived_relative_effort = float(activity_record["Perceived Relative Effort"] or 0)
    return activity


class Activity:
    """Provides storage for single activity metrics."""
    def __init__(self):
        self.activity_id = None
        self.date = None
        self.name = None
        self.activity_type = None
        self.elapsed_time = None
        self.distance = None
        self.filename = None
        self.moving_time = None
        self.max_speed = None
        self.average_speed = None
        self.elevation_gain = None
        self.elevation_low = None
        self.elevation_high = None
        self.max_grade = None
        self.average_grade = None
        self.perceived_exertion = None
        self.perceived_relative_effort = None


    def convert_to_imperial(self):
        """Converts all speeds and measures to imperial, assuming that they are curently metric."""
        self.distance = self.distance * 0.000621371 # convert meters to miles
        self.max_speed = self.max_speed * 2.237 # convert m/s to mph
        self.average_speed = self.average_speed * 2.237 # convert m/s to mph
        self.elevation_gain = self.elevation_gain * 3.28084 # convert meters to feet
        self.elevation_low = self.elevation_low * 3.28084 # convert meters to feet
        self.elevation_high = self.elevation_high * 3.28084 # convert meters to feet
        return self
